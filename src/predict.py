"""
Real-Time Inference Script for PhishNet-GNN
===========================================
End-to-end inference script that extracts features, resolves live DNS,
connects the new URL into the cached DGL heterogeneous graph, and
runs a forward pass to determine phishing risk.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List

import pandas as pd
import numpy as np
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

try:
    import torch
    import dgl
    HAS_PYTORCH = True
except Exception as e:
    logger.debug(f"PyTorch/DGL not available: {e}")
    HAS_PYTORCH = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.feature_extractor import extract_domain_features, get_feature_names, get_feature_descriptions
from src.data.dns_resolver import DNSResolver
from src.graph.graph_builder import DomainGraphBuilder


def predict_url(url: str) -> Dict[str, Any]:
    """
    Real-time inference for a single URL.
    1. Extracts 21 features and resolves live DNS.
    2. Connects the new URL node into the cached graph.
    3. Loads model weights and returns probability, verdict, and top risk factors.
    """
    logger.info(f"Analyzing URL: {url}")

    # 1. Clean URL and Extract Domain
    domain = url.lower().strip()
    domain = domain.replace('https://', '').replace('http://', '').rstrip('/')
    domain = domain.split('/')[0].split('?')[0]

    # 2. Resolve Live DNS
    dns_cache_path = str(PROJECT_ROOT / "data" / "dns_cache.db")
    with DNSResolver(cache_db=dns_cache_path) as resolver:
        dns_info = resolver.resolve_domain(domain)

    # 3. Extract 21 Features
    features = extract_domain_features(domain, dns_info=dns_info)

    # Identify Top 3 Risk Factors (Heuristic approximation of feature importance)
    top_factors = _get_top_risk_factors(features)

    # 4. GNN Graph Integration & Forward Pass
    if HAS_PYTORCH:
        try:
            prob, verdict = _run_gnn_forward_pass(domain, dns_info, features)
            # Only report DGL_RGCN after successful forward pass
            print("MODEL_MODE: DGL_RGCN")
            logger.info("MODEL_MODE: DGL_RGCN")
        except Exception as e:
            logger.warning(f"GNN forward pass failed: {e}")
            print("MODEL_MODE: SKLEARN_FALLBACK")
            logger.warning("MODEL_MODE: SKLEARN_FALLBACK")
            logger.warning("Falling back to heuristic scoring.")
            prob, verdict = _heuristic_scoring(features)
    else:
        print("MODEL_MODE: SKLEARN_FALLBACK")
        logger.info("MODEL_MODE: SKLEARN_FALLBACK")
        logger.info("PyTorch/DGL not installed. Using heuristic scoring.")
        prob, verdict = _heuristic_scoring(features)

    return {
        'url': url,
        'domain': domain,
        'probability': prob,
        'verdict': verdict,
        'top_risk_factors': top_factors,
        'features': features,
        'dns_info': dns_info
    }


# Global model cache for fast real-time inference
_CACHED_MODEL = None
_CACHED_MODEL_PATH = None


def _run_gnn_forward_pass(domain: str, dns_info: Dict, features: Dict) -> Tuple[float, str]:
    """Connects the domain to the cached graph and runs RGCN."""
    global _CACHED_MODEL, _CACHED_MODEL_PATH

    # A. Load cached dataset to reconstruct the graph context
    dataset_path = PROJECT_ROOT / "data" / "domains_dataset.csv"
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset not found at {dataset_path}. Run training first.")

    df = pd.read_csv(dataset_path)

    # Append the new domain to the dataframe if not already present
    if domain not in df['domain'].values:
        new_row = pd.DataFrame({'domain': [domain], 'label': [0], 'source': ['inference']})
        df = pd.concat([df, new_row], ignore_index=True)

    # Bulk-load DNS cache directly from SQLite in milliseconds
    db_path = str(PROJECT_ROOT / "data" / "dns_cache.db")
    with sqlite3.connect(db_path) as conn:
        dns_df = pd.read_sql_query("SELECT domain, ip_addresses, nameservers, dns_status FROM dns_cache", conn)

    # Ensure current domain's DNS is present in dns_df
    if domain not in dns_df['domain'].values and dns_info:
        new_dns_row = pd.DataFrame([{
            'domain': domain,
            'ip_addresses': json.dumps(dns_info.get('ip_addresses', [])),
            'nameservers': json.dumps(dns_info.get('nameservers', [])),
            'dns_status': dns_info.get('dns_status', 'failed')
        }])
        dns_df = pd.concat([dns_df, new_dns_row], ignore_index=True)

    # B. Load precomputed features from training cache, or fall back to zeros
    feature_cols = get_feature_names()
    cached_features_path = PROJECT_ROOT / "models" / "saved" / "domain_features.csv"

    if cached_features_path.exists():
        cached_df = pd.read_csv(cached_features_path)
        # Merge cached features with domain list; new domains will have NaN -> fill 0
        features_df = df[['domain']].merge(cached_df, on='domain', how='left')
        for col in feature_cols:
            if col not in features_df.columns:
                features_df[col] = 0.0
        features_df[feature_cols] = features_df[feature_cols].fillna(0.0)
    else:
        logger.warning("No cached features found at %s. Using zeros for background domains.", cached_features_path)
        features_df = pd.DataFrame({'domain': df['domain']})
        for col in feature_cols:
            features_df[col] = 0.0

    # Inject actual features for the target domain
    idx = features_df.index[features_df['domain'] == domain].tolist()[0]
    for k, v in features.items():
        if k in features_df.columns:
            features_df.at[idx, k] = v

    # Validate feature dimensions
    actual_feat_count = len([c for c in feature_cols if c in features_df.columns])
    if actual_feat_count != 21:
        raise ValueError(f"Feature dimension mismatch: expected 21, got {actual_feat_count}")

    # C. Build Graph
    builder = DomainGraphBuilder()
    builder.build_graph(df, dns_df, features_df)
    g = builder.to_dgl_graph(get_feature_names())

    # Find the node ID of our target domain
    domain_idx = builder.domain_to_idx[domain]

    # D. Load Model and Predict
    from src.models.gnn_model import PhishRGCN
    model_path = PROJECT_ROOT / "models" / "saved" / "phish_rgcn.pt"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained RGCN model not found at {model_path}. "
            f"Run training first: python main.py train --model gnn"
        )

    # Use cached model in memory if already loaded
    in_feats = {ntype: g.nodes[ntype].data['feat'].shape[1] for ntype in g.ntypes}
    if _CACHED_MODEL is None or _CACHED_MODEL_PATH != str(model_path):
        model = PhishRGCN(in_feats=in_feats, hidden_dim=128, num_classes=2, num_layers=3, dropout=0.3)
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'), weights_only=True))
        model.eval()
        _CACHED_MODEL = model
        _CACHED_MODEL_PATH = str(model_path)
    else:
        model = _CACHED_MODEL

    # E. Forward Pass
    feat_dict = {ntype: g.nodes[ntype].data['feat'] for ntype in g.ntypes}
    with torch.no_grad():
        logits = model(g, feat_dict)
        probs = torch.softmax(logits, dim=1)

    target_prob = probs[domain_idx, 1].item()
    verdict = 'PHISHING' if target_prob >= 0.5 else 'BENIGN'

    return target_prob, verdict


def _heuristic_scoring(features: Dict) -> Tuple[float, str]:
    """Fallback heuristic scoring when PyTorch is unavailable."""
    score = 0.0
    if features.get('entropy', 0) > 4.0: score += 0.15
    if features.get('suspicious_tld', 0) > 0: score += 0.20
    if features.get('contains_login_keywords', 0) > 0: score += 0.20
    brand_sim = features.get('brand_similarity', 20)
    if brand_sim <= 2:  # Include 0 (exact/leet brand match = high risk)
        score += 0.25
    elif brand_sim <= 4:
        score += 0.15
    if features.get('has_ip', 0) > 0: score += 0.20
    if features.get('is_punycode', 0) > 0: score += 0.15

    prob = min(1.0, score)
    verdict = 'PHISHING' if prob >= 0.5 else 'BENIGN'
    return prob, verdict


def _get_top_risk_factors(features: Dict) -> List[str]:
    """Extracts the top 3 risk factors based on feature values."""
    risks = []

    brand_sim = features.get('brand_similarity', 20)
    if brand_sim <= 2:  # Include 0 (exact/leet brand match = high risk)
        risks.append("High brand impersonation risk (similar to major brand)")
    elif brand_sim <= 4:
        risks.append("Moderate brand similarity (possible typo-squatting)")
    if features.get('contains_login_keywords', 0) > 0:
        risks.append("Contains deceptive login/security keywords")
    if features.get('has_ip', 0) > 0:
        risks.append("Contains raw IP address in URL")
    if features.get('suspicious_tld', 0) > 0:
        risks.append("Uses a TLD commonly associated with phishing")
    if features.get('entropy', 0) > 3.8:
        risks.append(f"High string randomness (Entropy: {features.get('entropy'):.2f})")
    if features.get('num_a_records', 0) == 0:
        risks.append("No active IP address (Offline or hidden infrastructure)")
    if features.get('is_punycode', 0) > 0:
        risks.append("Uses Punycode (homograph attack indicator)")

    # If safe, return safe reasons
    if not risks:
        if features.get('num_a_records', 0) > 0 and features.get('num_ns_records', 0) > 0:
            risks.append("Active and resolved DNS infrastructure")
        if features.get('entropy', 0) < 3.0:
            risks.append("Normal string entropy")
        risks.append("No suspicious lexical traits detected")

    return risks[:3]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Real-Time PhishNet-GNN Inference",
        usage="python src/predict.py [--domain URL]"
    )
    parser.add_argument(
        '--domain', type=str, default=None,
        help='URL or domain to analyze (e.g., "https://google.com")'
    )
    args = parser.parse_args()

    print("="*60)
    print("  Real-Time PhishNet-GNN Inference")
    print("="*60)

    if args.domain:
        test_urls = [args.domain]
    else:
        print("  No --domain provided. Running safe demo list.")
        test_urls = [
            "http://paypal-verification-update.com.tk",
            "https://google.com"
        ]

    for url in test_urls:
        res = predict_url(url)
        print(f"\n[ URL ] {res['url']}")
        print(f"   Probability  : {res['probability'] * 100:.2f}%")
        print(f"   Verdict      : {res['verdict']}")
        print(f"   Top 3 Risks  :")
        for r in res['top_risk_factors']:
            print(f"     - {r}")
    print("\n" + "="*60)