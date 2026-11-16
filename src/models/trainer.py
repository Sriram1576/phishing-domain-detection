"""
Training Pipeline Module (v2.0)
================================
Orchestrates the full PhishNet-GNN v2 training pipeline:

1. Collect or load domain dataset (real + synthetic fallback)
2. Resolve DNS records (A-records, NS-records) with caching
3. Extract lexical + DNS-aware features
4. Build heterogeneous domain-IP-NS graph
5. Train RGCN model on heterograph
6. Train baseline ML models for comparison
7. Evaluate and compare all models
8. Save results, models, and visualizations
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


class PhishNetTrainer:
    """End-to-end training pipeline for phishing domain detection v2.0."""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Configuration dictionary from config.yaml.
        """
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Paths
        self.data_dir = config.get('data', {}).get('output_dir', 'data')
        self.models_dir = config.get('paths', {}).get('models_dir', 'saved_models')
        self.results_dir = config.get('paths', {}).get('results_dir', 'results')

        # Create directories
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.results_dir, exist_ok=True)

        # Training params
        self.seed = config.get('training', {}).get('random_seed', 42)
        self.train_ratio = config.get('training', {}).get('train_ratio', 0.8)
        self.val_ratio = config.get('training', {}).get('val_ratio', 0.1)
        self.test_ratio = config.get('training', {}).get('test_ratio', 0.1)

        # Set seeds
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(self.seed)

        logger.info("PhishNetTrainer v2.0 initialized (device=%s)", self.device)

    # ── Step 1: Dataset Loading ────────────────────────────────────────

    def load_dataset(self) -> pd.DataFrame:
        """Load or collect domain dataset.

        Checks for existing CSV first. If not found, attempts real data
        collection (PhishTank + Tranco), falling back to synthetic generation.

        Returns:
            DataFrame with columns: domain, label, source.
        """
        dataset_file = self.config.get('data', {}).get('dataset_file', 'domains_dataset.csv')
        dataset_path = os.path.join(self.data_dir, dataset_file)

        if os.path.exists(dataset_path):
            logger.info("Loading existing dataset from %s", dataset_path)
            df = pd.read_csv(dataset_path)
            logger.info("Loaded %d domains", len(df))
            return df

        logger.info("Dataset not found. Collecting from online sources...")

        try:
            from src.data.dataset_collector import DatasetCollector

            num_mal = self.config.get('data', {}).get('num_malicious', 5000)
            num_ben = self.config.get('data', {}).get('num_benign', 5000)

            collector = DatasetCollector()
            df = collector.collect(num_malicious=num_mal, num_benign=num_ben)
            collector.save(df, dataset_path)
            return df

        except Exception as e:
            logger.warning("Online collection failed (%s). Using synthetic fallback.", e)

            from src.data.dataset_generator import PhishingDatasetGenerator

            num_legit = self.config.get('data', {}).get('num_legitimate_fallback', 3000)
            num_phish = self.config.get('data', {}).get('num_phishing_fallback', 3000)

            generator = PhishingDatasetGenerator(
                num_legit=num_legit, num_phishing=num_phish, seed=self.seed
            )
            df = generator.generate()

            # Add source column if missing
            if 'source' not in df.columns:
                df['source'] = 'synthetic'

            generator.save(df, output_path=dataset_path)
            return df

    # ── Step 2: DNS Resolution ─────────────────────────────────────────

    def resolve_dns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Resolve DNS A-records and NS-records for all domains.

        Uses SQLite caching to avoid redundant queries.

        Args:
            df: DataFrame with 'domain' column.

        Returns:
            DataFrame with columns: domain, ip_addresses, nameservers, dns_status.
        """
        dns_cache_path = os.path.join(
            self.data_dir,
            self.config.get('data', {}).get('dns_cache_db', 'dns_cache.db').replace('data/', '')
        )

        dns_cfg = self.config.get('dns', {})

        try:
            from src.data.dns_resolver import DNSResolver

            with DNSResolver(
                cache_db=dns_cache_path,
                timeout=dns_cfg.get('timeout', 3.0),
                max_retries=dns_cfg.get('max_retries', 2),
                nameservers=dns_cfg.get('nameservers'),
                rate_limit=dns_cfg.get('rate_limit', 50),
            ) as resolver:
                domains = df['domain'].tolist()
                dns_df = resolver.resolve_batch(
                    domains,
                    batch_size=dns_cfg.get('batch_size', 100),
                )
                logger.info(
                    "DNS resolution complete: %d resolved, %d failed",
                    (dns_df['dns_status'] != 'failed').sum(),
                    (dns_df['dns_status'] == 'failed').sum(),
                )
                return dns_df

        except ImportError:
            logger.warning("dnspython not installed. Creating empty DNS records.")
            return self._empty_dns_df(df['domain'].tolist())

        except Exception as e:
            logger.error("DNS resolution failed: %s. Using empty records.", e)
            return self._empty_dns_df(df['domain'].tolist())

    @staticmethod
    def _empty_dns_df(domains: List[str]) -> pd.DataFrame:
        """Create an empty DNS DataFrame when resolution is unavailable."""
        return pd.DataFrame({
            'domain': domains,
            'ip_addresses': ['[]'] * len(domains),
            'nameservers': ['[]'] * len(domains),
            'dns_status': ['failed'] * len(domains),
        })

    # ── Step 3: Feature Extraction ─────────────────────────────────────

    def extract_features(
        self, df: pd.DataFrame, dns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Extract lexical + DNS-aware features for all domains.

        Args:
            df: Domain dataset DataFrame.
            dns_df: DNS resolution DataFrame.

        Returns:
            DataFrame with domain + feature columns.
        """
        from src.data.feature_extractor import extract_features_batch

        # Build a lookup for DNS info
        dns_records = {}
        for _, row in dns_df.iterrows():
            domain = row['domain']
            try:
                ips = json.loads(row.get('ip_addresses', '[]'))
            except (json.JSONDecodeError, TypeError):
                ips = []
            try:
                nss = json.loads(row.get('nameservers', '[]'))
            except (json.JSONDecodeError, TypeError):
                nss = []

            dns_records[domain] = {
                'ip_addresses': ips,
                'nameservers': nss,
                'dns_status': row.get('dns_status', 'failed'),
            }

        features_df = extract_features_batch(
            df['domain'].tolist(),
            dns_records=dns_records,
        )

        logger.info("Extracted %d features for %d domains", 
                     len([c for c in features_df.columns if c != 'domain']),
                     len(features_df))
        return features_df

    # ── Step 4: Graph Building ─────────────────────────────────────────

    def build_graph(
        self, df: pd.DataFrame, dns_df: pd.DataFrame, features_df: pd.DataFrame
    ):
        from src.graph.graph_builder import DomainGraphBuilder
        from src.data.feature_extractor import get_feature_names

        builder = DomainGraphBuilder()
        builder.build_graph(df, dns_df, features_df)

        stats = builder.get_graph_stats()
        logger.info("Graph stats: %s", json.dumps(stats, indent=2, default=str))

        feature_cols = get_feature_names()
        feature_cols = [c for c in feature_cols if c in features_df.columns]

        dgl_graph = builder.to_dgl_graph(feature_cols)
        logger.info("DGL heterograph created with %d domain nodes", 
                     dgl_graph.num_nodes('domain'))

        return dgl_graph, builder, feature_cols


    def create_masks(self, num_nodes: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        indices = np.arange(num_nodes)
        np.random.shuffle(indices)

        n_train = int(num_nodes * self.train_ratio)
        n_val = int(num_nodes * self.val_ratio)

        train_idx = indices[:n_train]
        val_idx = indices[n_train:n_train + n_val]
        test_idx = indices[n_train + n_val:]

        train_mask = torch.zeros(num_nodes, dtype=torch.bool)
        val_mask = torch.zeros(num_nodes, dtype=torch.bool)
        test_mask = torch.zeros(num_nodes, dtype=torch.bool)

        train_mask[train_idx] = True
        val_mask[val_idx] = True
        test_mask[test_idx] = True

        return train_mask, val_mask, test_mask


    def train_rgcn(self, g, feature_cols: List[str]) -> Dict[str, Any]:
        from src.models.gnn_model import PhishRGCN, FocalLoss, EarlyStopping

        in_feats = {}
        for ntype in g.ntypes:
            if 'feat' in g.nodes[ntype].data:
                in_feats[ntype] = g.nodes[ntype].data['feat'].shape[1]
            else:
                in_feats[ntype] = 1

        rgcn_cfg = self.config.get('model', {}).get('rgcn', {})
        loss_cfg = self.config.get('model', {}).get('loss', {})

        model = PhishRGCN(
            in_feats=in_feats,
            hidden_dim=rgcn_cfg.get('hidden_dim', 128),
            num_classes=2,
            num_layers=rgcn_cfg.get('num_layers', 3),
            dropout=rgcn_cfg.get('dropout', 0.3)
        ).to(self.device)

        if loss_cfg.get('type', 'focal') == 'focal':
            criterion = FocalLoss(
                alpha=loss_cfg.get('focal_alpha', 0.25),
                gamma=loss_cfg.get('focal_gamma', 2.0),
            )
        else:
            criterion = nn.CrossEntropyLoss()

        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=rgcn_cfg.get('learning_rate', 0.005),
            weight_decay=rgcn_cfg.get('weight_decay', 5e-4)
        )

        g = g.to(self.device)

        best_model_path = os.path.join(self.models_dir, 'phish_rgcn.pt')
        early_stopping = EarlyStopping(
            patience=rgcn_cfg.get('patience', 20),
            path=best_model_path,
        )

        epochs = 50
        history = {'train_loss': [], 'val_loss': [], 'val_acc': []}

        logger.info("Training RGCN for up to %d epochs...", epochs)
        
        feat_dict = {ntype: g.nodes[ntype].data.get('feat', torch.ones(g.num_nodes(ntype), 1).to(self.device)) for ntype in g.ntypes}
        labels = g.nodes['domain'].data['label'].to(self.device)
        
        num_nodes = g.num_nodes('domain')
        train_mask, val_mask, test_mask = self.create_masks(num_nodes)
        train_mask, val_mask, test_mask = train_mask.to(self.device), val_mask.to(self.device), test_mask.to(self.device)

        for epoch in range(epochs):
            model.train()
            logits = model(g, feat_dict)
            loss = criterion(logits[train_mask], labels[train_mask])

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            model.eval()
            with torch.no_grad():
                val_logits = model(g, feat_dict)
                val_loss = criterion(val_logits[val_mask], labels[val_mask]).item()
                val_preds = val_logits[val_mask].argmax(dim=1)
                val_acc = (val_preds == labels[val_mask]).float().mean().item()

            history['train_loss'].append(loss.item())
            history['val_loss'].append(val_loss)
            history['val_acc'].append(val_acc)

            if (epoch + 1) % 10 == 0:
                logger.info("Epoch %03d | Train Loss: %.4f | Val Loss: %.4f | Val Acc: %.4f",
                            epoch + 1, loss.item(), val_loss, val_acc)

            if early_stopping(val_loss, model, epoch):
                logger.info("Early stopping triggered at epoch %d", epoch + 1)
                break

        model = early_stopping.load_best_model(model)
        model.eval()

        with torch.no_grad():
            test_logits = model(g, feat_dict)
            test_probs = torch.softmax(test_logits[test_mask], dim=1)[:, 1].cpu().numpy()
            test_preds = test_logits[test_mask].argmax(dim=1).cpu().numpy()
            test_labels = labels[test_mask].cpu().numpy()

        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        try:
            roc_auc = roc_auc_score(test_labels, test_probs)
        except ValueError:
            roc_auc = 0.5

        test_metrics = {
            'accuracy': accuracy_score(test_labels, test_preds),
            'precision': precision_score(test_labels, test_preds, zero_division=0),
            'recall': recall_score(test_labels, test_preds, zero_division=0),
            'f1_score': f1_score(test_labels, test_preds, zero_division=0),
            'roc_auc': roc_auc,
        }

        logger.info(
            "RGCN Test Results: acc=%.4f, prec=%.4f, rec=%.4f, f1=%.4f, roc_auc=%.4f",
            test_metrics['accuracy'], test_metrics['precision'],
            test_metrics['recall'], test_metrics['f1_score'], test_metrics['roc_auc']
        )

        return {
            'history': history,
            'test_metrics': test_metrics,
            'model_path': best_model_path,
        }

    # ── Step 7: Baseline Training ──────────────────────────────────────

    def train_baselines(
        self, features_df: pd.DataFrame, labels: np.ndarray
    ) -> Dict[str, Dict[str, Any]]:
        """Train scikit-learn baseline models.

        Args:
            features_df: Feature DataFrame (domain + feature cols).
            labels: Label array.

        Returns:
            Dict mapping model name to results.
        """
        from src.models.baseline import train_all_baselines
        from src.data.feature_extractor import get_feature_names

        feature_cols = get_feature_names()
        feature_cols = [c for c in feature_cols if c in features_df.columns]

        X = features_df[feature_cols].fillna(0).values
        y = labels

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_ratio, random_state=self.seed, stratify=y,
        )

        results = train_all_baselines(
            X_train, y_train, X_test, y_test,
            feature_names=feature_cols,
            cv_folds=self.config.get('model', {}).get('baseline', {}).get('cv_folds', 5),
            save_dir=self.models_dir,
        )

        return results

    # ── Step 8: Full Pipeline ──────────────────────────────────────────

    def run(self) -> Dict[str, Any]:
        """Run the complete training pipeline end-to-end.

        Returns:
            Dict with all results (GNN + baselines).
        """
        logger.info("=" * 60)
        logger.info("PhishNet-GNN v2.0 Training Pipeline")
        logger.info("=" * 60)

        # Step 1: Load dataset
        df = self.load_dataset()
        logger.info("Dataset: %d domains (%d malicious, %d benign)",
                     len(df), (df['label'] == 1).sum(), (df['label'] == 0).sum())

        # Step 2: DNS resolution
        dns_df = self.resolve_dns(df)

        # Step 3: Feature extraction
        features_df = self.extract_features(df, dns_df)

        # Step 3b: Save feature cache for inference
        from src.data.feature_extractor import get_feature_names
        feature_cols_for_cache = [c for c in get_feature_names() if c in features_df.columns]
        features_cache_path = os.path.join(self.models_dir, 'domain_features.csv')
        features_df[['domain'] + feature_cols_for_cache].to_csv(features_cache_path, index=False)
        logger.info("Saved feature cache to %s (%d domains, %d features)",
                     features_cache_path, len(features_df), len(feature_cols_for_cache))

        # Step 4: Build heterogeneous graph
        try:
            g, builder, feature_cols = self.build_graph(df, dns_df, features_df)
            has_graph = True
        except Exception as e:
            logger.warning("Graph construction failed: %s. Skipping GNN training.", e)
            has_graph = False

        results = {}

        # Step 5: Train RGCN
        if has_graph:
            try:
                print("MODEL_MODE: DGL_RGCN")
                logger.info("MODEL_MODE: DGL_RGCN")
                rgcn_results = self.train_rgcn(g, feature_cols)
                results['RGCN'] = rgcn_results['test_metrics']
                logger.info("RGCN training complete.")
            except Exception as e:
                logger.error("RGCN training failed: %s", e)
                print("MODEL_MODE: SKLEARN_FALLBACK")
                logger.info("MODEL_MODE: SKLEARN_FALLBACK")
        else:
            logger.warning("Skipping RGCN training (no graph available).")
            print("MODEL_MODE: SKLEARN_FALLBACK")
            logger.info("MODEL_MODE: SKLEARN_FALLBACK")

        # Step 6: Train baselines
        try:
            labels = df.set_index('domain').loc[features_df['domain']]['label'].values
            baseline_results = self.train_baselines(features_df, labels)
            for name, result in baseline_results.items():
                results[name] = result['metrics']
        except Exception as e:
            logger.error("Baseline training failed: %s", e)

        # Step 7: Save comparison
        comparison_path = os.path.join(self.results_dir, 'model_comparison.json')
        # Filter out non-serializable items
        serializable = {}
        for model_name, metrics in results.items():
            serializable[model_name] = {
                k: float(v) if isinstance(v, (int, float, np.integer, np.floating)) else v
                for k, v in metrics.items()
                if isinstance(v, (int, float, str, np.integer, np.floating))
            }

        with open(comparison_path, 'w') as f:
            json.dump(serializable, f, indent=2)
        logger.info("Model comparison saved to %s", comparison_path)

        # Print comparison table
        self._print_comparison(serializable)

        # Save graph visualization data
        if has_graph:
            graph_json_path = os.path.join(self.results_dir, 'graph_data.json')
            with open(graph_json_path, 'w') as f:
                json.dump(builder.to_json(max_nodes=200), f)
            logger.info("Graph visualization data saved to %s", graph_json_path)

        logger.info("=" * 60)
        logger.info("Training pipeline complete!")
        logger.info("=" * 60)

        return results

    @staticmethod
    def _print_comparison(results: Dict[str, Dict[str, float]]) -> None:
        """Print a formatted model comparison table."""
        print("\n" + "=" * 80)
        print("  Model Comparison Results")
        print("=" * 80)
        print(f"  {'Model':<25s} {'Accuracy':>10s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s} {'ROC-AUC':>10s}")
        print("-" * 80)
        for name, metrics in results.items():
            print(
                f"  {name:<25s} "
                f"{metrics.get('accuracy', 0):>10.4f} "
                f"{metrics.get('precision', 0):>10.4f} "
                f"{metrics.get('recall', 0):>10.4f} "
                f"{metrics.get('f1_score', 0):>10.4f} "
                f"{metrics.get('roc_auc', 0):>10.4f}"
            )
        print("=" * 80 + "\n")
