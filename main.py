#!/usr/bin/env python3
"""
PhishNet-GNN v2.0: Real-Time Phishing Domain Detection via Graph Neural Networks
=================================================================================

Main entry point. Supports:
    python main.py generate-data    # Collect real or generate synthetic domains
    python main.py train            # Train RGCN + baseline models
    python main.py evaluate         # Show evaluation results
    python main.py serve            # Start Flask REST API
    python main.py analyze --domain example.com   # Quick heuristic analysis
    python main.py infer --domain example.com     # Full GNN inference pipeline
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict

import yaml

# ── Project Root ───────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Banner ─────────────────────────────────────────────────────────────────
BANNER = """
  PhishNet-GNN v{version}
  Real-Time Phishing Domain Detection via Graph Neural Networks
  Architecture: Heterogeneous Graph (Domain-IP-NS) + RGCN
"""


# ── Configuration ──────────────────────────────────────────────────────────

def load_config(config_path=None):
    """Load the YAML configuration file."""
    if config_path is None:
        config_path = PROJECT_ROOT / "config.yaml"
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def setup_logging(config):
    """Configure project-wide logging."""
    logs_dir = PROJECT_ROOT / config.get("paths", {}).get("logs_dir", "logs/")
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "phishnet.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(str(log_file), encoding="utf-8"),
        ],
    )
    logger = logging.getLogger("PhishNet-GNN")
    logger.info("Logging initialised - log file: %s", log_file)
    return logger


def ensure_directories(config):
    """Create all required output directories."""
    for key in ['output_dir']:
        d = config.get('data', {}).get(key, 'data/')
        (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)
    for key in ['models_dir', 'results_dir', 'logs_dir']:
        d = config.get('paths', {}).get(key, '')
        if d:
            (PROJECT_ROOT / d).mkdir(parents=True, exist_ok=True)


# ── Subcommand Handlers ───────────────────────────────────────────────────

def cmd_generate_data(args, config, logger):
    """Collect real datasets or generate synthetic domains."""
    logger.info("Starting data collection...")

    from src.data.dataset_collector import DatasetCollector

    data_cfg = config.get("data", {})
    output_dir = str(PROJECT_ROOT / data_cfg.get("output_dir", "data/"))
    dataset_file = data_cfg.get("dataset_file", "domains_dataset.csv")
    output_path = os.path.join(output_dir, dataset_file)

    collector = DatasetCollector()
    df = collector.collect(
        num_malicious=data_cfg.get("num_malicious", 5000),
        num_benign=data_cfg.get("num_benign", 5000),
    )
    saved_path = collector.save(df, output_path)

    logger.info("Dataset saved to %s (%d rows)", saved_path, len(df))
    print(f"\n[+] Dataset collected: {len(df)} domains")
    print(f"    Malicious: {(df['label'] == 1).sum()}")
    print(f"    Benign:    {(df['label'] == 0).sum()}")
    if 'source' in df.columns:
        print(f"    Sources:   {df['source'].value_counts().to_dict()}")
    print(f"    Saved to:  {saved_path}\n")


def cmd_train(args, config, logger):
    """Run the full training pipeline."""
    model_choice = getattr(args, "model", "all")
    logger.info("Training pipeline started (model=%s)...", model_choice)

    from src.models.trainer import PhishNetTrainer

    # Resolve paths to absolute
    config['data']['output_dir'] = str(PROJECT_ROOT / config.get('data', {}).get('output_dir', 'data/'))
    config['paths']['models_dir'] = str(PROJECT_ROOT / config.get('paths', {}).get('models_dir', 'saved_models/'))
    config['paths']['results_dir'] = str(PROJECT_ROOT / config.get('paths', {}).get('results_dir', 'results/'))

    trainer = PhishNetTrainer(config=config)
    results = trainer.run()

    logger.info("Training complete. %d models evaluated.", len(results))


def cmd_evaluate(args, config, logger):
    """Show evaluation results from the last training run."""
    logger.info("Evaluation started...")

    results_dir = PROJECT_ROOT / config.get("paths", {}).get("results_dir", "results/")
    comparison_path = results_dir / "model_comparison.json"

    if comparison_path.exists():
        import json
        with open(comparison_path, 'r') as f:
            comparison = json.load(f)

        print("\n" + "=" * 70)
        print("  Model Comparison Results")
        print("=" * 70)
        print(f"  {'Model':<25s} {'Accuracy':>10s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s}")
        print("-" * 70)
        for name, metrics in comparison.items():
            print(
                f"  {name:<25s} "
                f"{metrics.get('accuracy', 0):>10.4f} "
                f"{metrics.get('precision', 0):>10.4f} "
                f"{metrics.get('recall', 0):>10.4f} "
                f"{metrics.get('f1_score', 0):>10.4f}"
            )
        print("=" * 70 + "\n")
    else:
        logger.warning("No results found at %s", comparison_path)
        print("\n[!] No evaluation results found. Train models first:")
        print("    python main.py train\n")


def cmd_serve(args, config, logger):
    """Start the Flask REST API server."""
    from src.api.server import create_app

    api_cfg = config.get("api", {})
    host = getattr(args, "host", None) or api_cfg.get("host", "0.0.0.0")
    port = getattr(args, "port", None) or api_cfg.get("port", 5000)
    debug = api_cfg.get("debug", False)

    logger.info("Starting API server on %s:%d...", host, port)
    print(f"\n  API Server: http://localhost:{port}")
    print(f"  Dashboard:  Open dashboard/index.html in your browser")
    print(f"  Health:     http://localhost:{port}/api/health\n")

    app = create_app(config=config)
    app.run(host=host, port=port, debug=debug, threaded=True)


def cmd_analyze(args, config, logger):
    """Quick heuristic analysis of a single domain."""
    domain = args.domain
    logger.info("Analyzing domain: %s", domain)

    from src.data.feature_extractor import extract_domain_features

    features = extract_domain_features(domain)

    # Heuristic risk scoring
    risk_score = _heuristic_risk_score(features)

    if risk_score >= 70:
        classification, icon = "PHISHING", "[!]"
    elif risk_score >= 40:
        classification, icon = "SUSPICIOUS", "[?]"
    else:
        classification, icon = "LEGITIMATE", "[+]"

    print("\n" + "=" * 60)
    print(f"  Domain Analysis Report: {domain}")
    print("=" * 60)
    print(f"  Prediction : {icon} {classification}")
    print(f"  Risk Score : {risk_score:.1f} / 100")
    print(f"  Method     : Heuristic (no DNS)")
    print("-" * 60)
    print("  Extracted Features:")
    for key, value in features.items():
        if isinstance(value, float):
            print(f"    - {key:<30s} {value:.4f}")
        else:
            print(f"    - {key:<30s} {value}")
    print("=" * 60 + "\n")


def cmd_infer(args, config, logger):
    """Full GNN inference pipeline: DNS + features + model."""
    domain = args.domain
    logger.info("Running full inference for: %s", domain)

    # Resolve paths
    models_dir = str(PROJECT_ROOT / config.get('paths', {}).get('models_dir', 'models/saved/'))
    data_dir = str(PROJECT_ROOT / config.get('data', {}).get('output_dir', 'data/'))

    from src.inference import PhishNetInference

    engine = PhishNetInference(
        models_dir=models_dir,
        data_dir=data_dir,
        config=config,
    )

    result = engine.analyze(domain)

    # Display
    risk = result['risk_score']
    cls = result['classification']
    if cls == "PHISHING":
        icon = "[!]"
    elif cls == "SUSPICIOUS":
        icon = "[?]"
    else:
        icon = "[+]"

    print("\n" + "=" * 60)
    print(f"  Domain Inference Report: {domain}")
    print("=" * 60)
    print(f"  Prediction  : {icon} {cls}")
    print(f"  Risk Score  : {risk:.1f} / 100")
    print(f"  Confidence  : {result['confidence']:.1f}%")
    print(f"  Model Used  : {result['model_used']}")
    print("-" * 60)

    # DNS Info
    dns = result.get('dns_info', {})
    ips = dns.get('ip_addresses', [])
    nss = dns.get('nameservers', [])
    print(f"  DNS Status  : {dns.get('dns_status', 'unknown')}")
    print(f"  IP Addresses: {', '.join(ips) if ips else 'none'}")
    print(f"  Nameservers : {', '.join(nss) if nss else 'none'}")
    print("-" * 60)

    # Key features
    features = result.get('features', {})
    print("  Key Features:")
    for key in ['entropy', 'brand_similarity', 'suspicious_tld',
                'contains_login_keywords', 'domain_length', 'digit_ratio',
                'num_a_records', 'num_ns_records']:
        val = features.get(key, 'N/A')
        if isinstance(val, float):
            print(f"    - {key:<30s} {val:.4f}")
        else:
            print(f"    - {key:<30s} {val}")
    print("=" * 60 + "\n")


def _heuristic_risk_score(features):
    """Calculate risk score using heuristic rules."""
    score = 0.0
    indicators = 0

    if features.get('entropy', 0) > 4.0:
        score += 15; indicators += 1
    elif features.get('entropy', 0) > 3.5:
        score += 8

    if features.get('suspicious_tld', 0) > 0:
        score += 20; indicators += 1
    if features.get('domain_length', 0) > 30:
        score += 12; indicators += 1
    elif features.get('domain_length', 0) > 20:
        score += 5
    if features.get('subdomain_count', 0) > 2:
        score += 15; indicators += 1
    elif features.get('subdomain_count', 0) > 1:
        score += 5
    if features.get('contains_login_keywords', 0) > 0:
        score += 18; indicators += 1

    brand = features.get('brand_similarity', 20)
    if 1 <= brand <= 3:
        score += 25; indicators += 1

    if features.get('hyphen_count', 0) > 2:
        score += 10
    elif features.get('hyphen_count', 0) > 0:
        score += 3
    if features.get('digit_ratio', 0) > 0.3:
        score += 8
    elif features.get('digit_count', 0) > 0 and features.get('digit_ratio', 0) > 0.05:
        score += 4
    if features.get('is_punycode', 0) > 0:
        score += 15; indicators += 1
    if features.get('consonant_sequence', 0) > 5:
        score += 10
    if features.get('has_ip', 0) > 0:
        score += 20; indicators += 1

    if indicators >= 3:
        score += 15
    elif indicators >= 2:
        score += 5

    return min(100, max(0, score))


# ── Argument Parser ────────────────────────────────────────────────────────

def build_parser():
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="phishnet-gnn",
        description="PhishNet-GNN v2.0: Real-Time Phishing Domain Detection via Graph Neural Networks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python main.py generate-data\n"
            "  python main.py train\n"
            "  python main.py evaluate\n"
            "  python main.py serve --port 8080\n"
            "  python main.py analyze --domain suspicious-site.com\n"
            "  python main.py infer --domain suspicious-site.com\n"
        ),
    )
    parser.add_argument("--config", type=str, default=None, help="Path to config.yaml")

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # generate-data
    sp = sub.add_parser("generate-data", help="Collect/generate domain dataset")
    sp.set_defaults(func=cmd_generate_data)

    # train
    sp = sub.add_parser("train", help="Train RGCN + baseline models")
    sp.add_argument("--model", choices=["rgcn", "baseline", "all"], default="all")
    sp.set_defaults(func=cmd_train)

    # evaluate
    sp = sub.add_parser("evaluate", help="Show evaluation results")
    sp.set_defaults(func=cmd_evaluate)

    # serve
    sp = sub.add_parser("serve", help="Start Flask REST API server")
    sp.add_argument("--host", type=str, default=None)
    sp.add_argument("--port", type=int, default=None)
    sp.set_defaults(func=cmd_serve)

    # analyze (quick heuristic)
    sp = sub.add_parser("analyze", help="Quick heuristic domain analysis")
    sp.add_argument("--domain", required=True, help="Domain to analyze")
    sp.set_defaults(func=cmd_analyze)

    # infer (full pipeline)
    sp = sub.add_parser("infer", help="Full inference: DNS + features + GNN model")
    sp.add_argument("--domain", required=True, help="Domain to analyze")
    sp.set_defaults(func=cmd_infer)

    return parser


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    """Application entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    config = load_config(args.config)

    version = config.get("project", {}).get("version", "2.0.0")
    print(BANNER.format(version=version))

    logger = setup_logging(config)
    ensure_directories(config)

    logger.info("PhishNet-GNN v%s", version)

    try:
        args.func(args, config, logger)
    except KeyboardInterrupt:
        logger.warning("Interrupted by user.")
        sys.exit(130)
    except Exception as exc:
        logger.exception("Fatal error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
