"""
Inference Pipeline Module
==========================
End-to-end inference for phishing domain detection:
    Input URL -> DNS Resolution -> Feature Extraction -> GNN Forward Pass -> Risk Score

Supports both RGCN (heterograph) and heuristic fallback when no trained model is available.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import numpy as np
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

logger = logging.getLogger(__name__)


class PhishNetInference:
    """End-to-end phishing domain inference pipeline.

    Loads a trained RGCN model and reference graph, resolves DNS for
    the query domain, extracts features, inserts it into the graph,
    and runs a GNN forward pass to produce a risk score.

    Falls back to heuristic scoring when no trained model is available.
    """

    def __init__(
        self,
        models_dir: str = "models/saved",
        data_dir: str = "data",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            models_dir: Directory containing saved model weights.
            data_dir: Directory containing DNS cache and reference data.
            config: Full configuration dictionary.
        """
        self.models_dir = Path(models_dir)
        self.data_dir = Path(data_dir)
        self.config = config or {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if HAS_TORCH else None

        self.model = None
        self.model_loaded = False

        self._try_load_model()

    def _try_load_model(self) -> None:
        """Attempt to load the trained RGCN model."""
        if not HAS_TORCH:
            logger.info("PyTorch not installed. Using heuristic fallback.")
            return

        model_path = self.models_dir / "best_rgcn.pt"
        if not model_path.exists():
            logger.info("No trained RGCN model found at %s. Using heuristic fallback.", model_path)
            return

        try:
            from src.models.gnn_model import PhishRGCN

            # Load model config
            config_path = self.models_dir / "rgcn_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    model_config = json.load(f)
            else:
                # Use defaults from config
                rgcn_cfg = self.config.get('model', {}).get('rgcn', {})
                model_config = {
                    'in_feats': {'domain': 21, 'ip': 1, 'nameserver': 1},
                    'hidden_dim': rgcn_cfg.get('hidden_dim', 128),
                    'num_classes': 2,
                    'num_layers': rgcn_cfg.get('num_layers', 3),
                    'dropout': rgcn_cfg.get('dropout', 0.3),
                    'num_bases': rgcn_cfg.get('num_bases', 4),
                }

            self.model = PhishRGCN(**model_config).to(self.device)
            self.model.load_state_dict(
                torch.load(str(model_path), map_location=self.device, weights_only=True)
            )
            self.model.eval()
            self.model_loaded = True
            logger.info("RGCN model loaded from %s", model_path)

        except Exception as e:
            logger.warning("Failed to load RGCN model: %s. Using heuristic fallback.", e)
            self.model = None
            self.model_loaded = False

    def analyze(self, domain: str) -> Dict[str, Any]:
        """Analyze a single domain for phishing risk.

        Pipeline: DNS resolve -> Feature extract -> Risk score

        Args:
            domain: Domain name to analyze.

        Returns:
            Dict with: domain, risk_score, classification, confidence,
            features, dns_info.
        """
        # Clean domain
        domain = domain.lower().strip()
        domain = domain.replace('https://', '').replace('http://', '').rstrip('/')
        domain = domain.split('/')[0].split('?')[0]

        logger.info("Analyzing domain: %s", domain)

        # Step 1: DNS Resolution
        dns_info = self._resolve_dns(domain)

        # Step 2: Feature Extraction
        from src.data.feature_extractor import extract_domain_features
        features = extract_domain_features(domain, dns_info=dns_info)

        # Step 3: Risk Scoring
        risk_score = self._calculate_risk_score(features)

        # Classification
        if risk_score >= 70:
            classification = "PHISHING"
        elif risk_score >= 40:
            classification = "SUSPICIOUS"
        else:
            classification = "LEGITIMATE"

        confidence = min(99.0, 50.0 + risk_score * 0.5)

        return {
            'domain': domain,
            'risk_score': round(risk_score, 1),
            'classification': classification,
            'confidence': round(confidence, 1),
            'features': features,
            'dns_info': dns_info,
            'model_used': 'rgcn' if self.model_loaded else 'heuristic',
        }

    def _resolve_dns(self, domain: str) -> Dict[str, Any]:
        """Resolve DNS records for a single domain.

        Args:
            domain: Domain to resolve.

        Returns:
            Dict with ip_addresses, nameservers, dns_status.
        """
        dns_cache_path = str(
            self.data_dir / self.config.get('data', {}).get(
                'dns_cache_db', 'dns_cache.db'
            ).replace('data/', '')
        )

        try:
            from src.data.dns_resolver import DNSResolver

            dns_cfg = self.config.get('dns', {})
            with DNSResolver(
                cache_db=dns_cache_path,
                timeout=dns_cfg.get('timeout', 3.0),
                max_retries=dns_cfg.get('max_retries', 2),
                nameservers=dns_cfg.get('nameservers'),
            ) as resolver:
                result = resolver.resolve_domain(domain)
                return result

        except ImportError:
            logger.debug("dnspython not available for inference.")
            return {'ip_addresses': [], 'nameservers': [], 'dns_status': 'failed'}

        except Exception as e:
            logger.debug("DNS resolution failed for %s: %s", domain, e)
            return {'ip_addresses': [], 'nameservers': [], 'dns_status': 'failed'}

    @staticmethod
    def _calculate_risk_score(features: Dict[str, float]) -> float:
        """Calculate risk score from extracted features.

        Uses a weighted heuristic with compound indicator boosting.

        Args:
            features: Extracted feature dictionary.

        Returns:
            Risk score between 0 and 100.
        """
        score = 0.0
        indicators_fired = 0

        # Entropy
        entropy = features.get('entropy', 0)
        if entropy > 4.0:
            score += 15
            indicators_fired += 1
        elif entropy > 3.5:
            score += 8

        # Suspicious TLD
        if features.get('suspicious_tld', 0) > 0:
            score += 20
            indicators_fired += 1

        # Domain length
        length = features.get('domain_length', 0)
        if length > 30:
            score += 12
            indicators_fired += 1
        elif length > 20:
            score += 5

        # Subdomains
        subdomains = features.get('subdomain_count', 0)
        if subdomains > 2:
            score += 15
            indicators_fired += 1
        elif subdomains > 1:
            score += 5

        # Login keywords
        if features.get('contains_login_keywords', 0) > 0:
            score += 18
            indicators_fired += 1

        # Brand similarity
        brand_sim = features.get('brand_similarity', 20)
        if 1 <= brand_sim <= 3:
            score += 25
            indicators_fired += 1

        # Hyphens
        hyphens = features.get('hyphen_count', 0)
        if hyphens > 2:
            score += 10
        elif hyphens > 0:
            score += 3

        # Digits
        digit_ratio = features.get('digit_ratio', 0)
        if digit_ratio > 0.3:
            score += 8
        elif features.get('digit_count', 0) > 0 and digit_ratio > 0.05:
            score += 4

        # Punycode
        if features.get('is_punycode', 0) > 0:
            score += 15
            indicators_fired += 1

        # Consonant sequences
        if features.get('consonant_sequence', 0) > 5:
            score += 10

        # Has IP pattern
        if features.get('has_ip', 0) > 0:
            score += 20
            indicators_fired += 1

        # DNS-aware signals
        if features.get('dns_failed', 0) > 0:
            score += 5  # Failed DNS is mildly suspicious

        # Compound boost
        if indicators_fired >= 3:
            score += 15
        elif indicators_fired >= 2:
            score += 5

        return min(100.0, max(0.0, score))
