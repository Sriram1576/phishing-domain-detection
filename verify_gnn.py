import os
import sys
import yaml
import json
import logging
import torch

# Initialize minimal logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def verify_setup():
    print("=" * 60)
    print("VERIFYING DGL & PYTORCH ENVIRONMENT")
    print("=" * 60)
    
    try:
        import dgl
        import networkx
        import sklearn
    except ImportError as e:
        print(f"FAILED TO IMPORT: {e}")
        print("Please ensure you are in the Python 3.11 virtual environment with DGL installed.")
        sys.exit(1)
        
    print(f"PyTorch Version: {torch.__version__}")
    print(f"DGL Version:     {dgl.__version__}")
    print("Imports successful!")
    print("\n")
    
def verify_pipeline():
    print("=" * 60)
    print("VERIFYING GRAPH CONSTRUCTION & TRAINING")
    print("=" * 60)
    
    # Imports inside to rely on local project structure
    import pandas as pd
    from src.models.trainer import PhishNetTrainer
    from src.graph.graph_builder import DomainGraphBuilder
    
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        
    trainer = PhishNetTrainer(config)
    
    # Load dataset using the trainer pipeline (no separate CSVs needed)
    print("0. Loading dataset via trainer pipeline...")
    df = trainer.load_dataset()
    print(f"   Dataset: {len(df)} domains ({(df['label']==1).sum()} phishing, {(df['label']==0).sum()} benign)")
    
    # Resolve DNS using the trainer pipeline
    print("   Resolving DNS (cached)...")
    dns_df = trainer.resolve_dns(df)
    
    # Extract features using the trainer pipeline
    print("   Extracting features...")
    features_df = trainer.extract_features(df, dns_df)
    
    # Test Graph Builder directly
    print("1. Testing Graph Builder...")
    g, builder, feature_cols = trainer.build_graph(df, dns_df, features_df)
    
    print(f"   Node Types: {g.ntypes}")
    print(f"   Canonical Edge Types: {g.canonical_etypes}")
    
    feat_shape = g.nodes['domain'].data['feat'].shape
    print(f"   Domain Features Shape: {feat_shape} (Expected: [N, 21])")
    
    # Print edge counts
    print("   Edge Counts:")
    for etype in g.canonical_etypes:
        print(f"     {etype}: {g.num_edges(etype)}")
    
    # Save features for inference caching (Fix 6)
    features_cache_path = os.path.join(trainer.models_dir, 'domain_features.csv')
    features_with_domain = features_df[['domain'] + feature_cols].copy()
    features_with_domain.to_csv(features_cache_path, index=False)
    print(f"   Saved feature cache: {features_cache_path} ({len(features_with_domain)} rows)")
    
    # Train RGCN
    print("\n2. Training DGL RGCN Model...")
    results = trainer.train_rgcn(g, feature_cols)
    
    print("\n3. Training Metrics:")
    metrics = results['test_metrics']
    for k, v in metrics.items():
        if k != 'confusion_matrix':
            print(f"   - {k}: {v:.4f}")
    print(f"   MODEL_MODE: DGL_RGCN")
            
    # Re-evaluate the model to get the confusion matrix
    from src.models.gnn_model import PhishRGCN
    import torch.nn.functional as F
    from sklearn.metrics import confusion_matrix
    
    in_feats = {}
    for ntype in g.ntypes:
        if 'feat' in g.nodes[ntype].data:
            in_feats[ntype] = g.nodes[ntype].data['feat'].shape[1]
        else:
            in_feats[ntype] = 1
            
    model = PhishRGCN(in_feats=in_feats)
    model_path = os.path.join(trainer.models_dir, 'phish_rgcn.pt')
    if not os.path.exists(model_path):
        print(f"ERROR: Model file not found at {model_path}")
        sys.exit(1)
        
    model.load_state_dict(torch.load(model_path, weights_only=True))
    model.eval()
    
    feat_dict = {ntype: g.nodes[ntype].data.get('feat', torch.ones(g.num_nodes(ntype), 1)) for ntype in g.ntypes}
    with torch.no_grad():
        logits = model(g, feat_dict)
        preds = logits.argmax(dim=1).numpy()
        labels = g.nodes['domain'].data['label'].numpy()
        
    cm = confusion_matrix(labels, preds)
    print("\n   Confusion Matrix:")
    print(f"   [[{cm[0][0]}, {cm[0][1]}]")
    print(f"    [{cm[1][0]}, {cm[1][1]}]]")
        
    print("\n")
    
def verify_inference():
    print("=" * 60)
    print("VERIFYING INFERENCE PIPELINE")
    print("=" * 60)
    
    from src.predict import predict_url
    
    test_url = "http://paypal-verification-update.com.tk"
    print(f"Running inference on: {test_url}")
    
    # This will print MODEL_MODE
    result = predict_url(test_url)
    
    print(f"\nVerdict: {result['verdict']}")
    print(f"Probability: {result['probability']:.2f}")
    
if __name__ == "__main__":
    verify_setup()
    verify_pipeline()
    verify_inference()
    print("\nVerification Complete!")
