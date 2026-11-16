"""
Baseline Models Module
======================
Scikit-Learn baseline classifiers for phishing domain detection.
Provides a comparison benchmark against the GNN model.

Models:
- Random Forest
- Gradient Boosting
- Logistic Regression
- Support Vector Machine (SVC)
"""

import os
import logging
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report,
    confusion_matrix
)

logger = logging.getLogger(__name__)


# Hyperparameter grids for each model
PARAM_GRIDS = {
    'RandomForest': {
        'clf__n_estimators': [100, 200],
        'clf__max_depth': [8, 12, None],
        'clf__min_samples_split': [2, 5],
        'clf__min_samples_leaf': [1, 2],
    },
    'GradientBoosting': {
        'clf__n_estimators': [100, 200],
        'clf__max_depth': [4, 6, 8],
        'clf__learning_rate': [0.05, 0.1],
        'clf__subsample': [0.8, 1.0],
    },
    'LogisticRegression': {
        'clf__C': [0.01, 0.1, 1.0, 10.0],
        'clf__penalty': ['l2'],
        'clf__max_iter': [1000],
    },
    'SVM': {
        'clf__C': [0.1, 1.0, 10.0],
        'clf__kernel': ['rbf'],
        'clf__gamma': ['scale', 'auto'],
    },
}


def create_model_pipeline(model_name: str) -> Pipeline:
    """
    Create a scikit-learn Pipeline with StandardScaler and classifier.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Scikit-learn Pipeline
    """
    classifiers = {
        'RandomForest': RandomForestClassifier(random_state=42, n_jobs=-1),
        'GradientBoosting': GradientBoostingClassifier(random_state=42),
        'LogisticRegression': LogisticRegression(random_state=42, max_iter=1000),
        'SVM': SVC(random_state=42, probability=True),
    }
    
    if model_name not in classifiers:
        raise ValueError(f"Unknown model: {model_name}. Choose from {list(classifiers.keys())}")
    
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', classifiers[model_name])
    ])
    
    return pipeline


def train_baseline(
    model_name: str,
    X_train: np.ndarray,
    y_train: np.ndarray,
    cv_folds: int = 5,
    use_grid_search: bool = True
) -> Tuple[Pipeline, Dict[str, float]]:
    """
    Train a single baseline model with optional hyperparameter tuning.
    
    Args:
        model_name: Name of the model to train
        X_train: Training features
        y_train: Training labels
        cv_folds: Number of cross-validation folds
        use_grid_search: Whether to use GridSearchCV for hyperparameter tuning
        
    Returns:
        Tuple of (trained pipeline, cross-validation scores)
    """
    logger.info(f"Training {model_name}...")
    
    pipeline = create_model_pipeline(model_name)
    
    if use_grid_search and model_name in PARAM_GRIDS:
        grid_search = GridSearchCV(
            pipeline,
            PARAM_GRIDS[model_name],
            cv=cv_folds,
            scoring='f1',
            n_jobs=-1,
            verbose=0,
            refit=True
        )
        grid_search.fit(X_train, y_train)
        best_pipeline = grid_search.best_estimator_
        
        logger.info(f"  Best params: {grid_search.best_params_}")
        logger.info(f"  Best CV F1: {grid_search.best_score_:.4f}")
        
        cv_scores = {
            'best_cv_f1': grid_search.best_score_,
            'best_params': str(grid_search.best_params_)
        }
        
        return best_pipeline, cv_scores
    else:
        pipeline.fit(X_train, y_train)
        
        # Cross-validation scores
        cv_f1 = cross_val_score(pipeline, X_train, y_train, cv=cv_folds, scoring='f1')
        cv_scores = {
            'mean_cv_f1': np.mean(cv_f1),
            'std_cv_f1': np.std(cv_f1)
        }
        
        return pipeline, cv_scores


def evaluate_model(
    model: Pipeline,
    X_test: np.ndarray,
    y_test: np.ndarray,
    model_name: str = "Model"
) -> Dict[str, float]:
    """
    Evaluate a trained model on test data.
    
    Args:
        model: Trained model pipeline
        X_test: Test features
        y_test: Test labels
        model_name: Name for logging
        
    Returns:
        Dictionary of evaluation metrics
    """
    y_pred = model.predict(X_test)
    
    # Get probabilities if available
    y_prob = None
    if hasattr(model, 'predict_proba'):
        try:
            y_prob = model.predict_proba(X_test)[:, 1]
        except Exception:
            pass
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, zero_division=0),
        'recall': recall_score(y_test, y_pred, zero_division=0),
        'f1_score': f1_score(y_test, y_pred, zero_division=0),
    }
    
    if y_prob is not None:
        try:
            metrics['auc_roc'] = roc_auc_score(y_test, y_prob)
        except ValueError:
            metrics['auc_roc'] = 0.0
    
    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
    metrics['true_positives'] = int(tp)
    metrics['true_negatives'] = int(tn)
    metrics['false_positives'] = int(fp)
    metrics['false_negatives'] = int(fn)
    
    logger.info(f"  {model_name} Results:")
    logger.info(f"    Accuracy:  {metrics['accuracy']:.4f}")
    logger.info(f"    Precision: {metrics['precision']:.4f}")
    logger.info(f"    Recall:    {metrics['recall']:.4f}")
    logger.info(f"    F1-Score:  {metrics['f1_score']:.4f}")
    if 'auc_roc' in metrics:
        logger.info(f"    AUC-ROC:   {metrics['auc_roc']:.4f}")
    
    return metrics


def get_feature_importance(
    model: Pipeline,
    feature_names: List[str],
    model_name: str = "Model"
) -> Optional[pd.DataFrame]:
    """
    Extract feature importance from tree-based models.
    
    Args:
        model: Trained pipeline
        feature_names: List of feature names
        model_name: Name for the output
        
    Returns:
        DataFrame with feature importances sorted by importance, or None
    """
    clf = model.named_steps['clf']
    
    if hasattr(clf, 'feature_importances_'):
        importances = clf.feature_importances_
        df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances,
            'model': model_name
        }).sort_values('importance', ascending=False)
        
        logger.info(f"\n  Top 10 features for {model_name}:")
        for _, row in df.head(10).iterrows():
            logger.info(f"    {row['feature']:<30s} {row['importance']:.4f}")
        
        return df
    
    return None


def train_all_baselines(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    y_test: np.ndarray,
    feature_names: List[str],
    cv_folds: int = 5,
    save_dir: Optional[str] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Train and evaluate all baseline models.
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        feature_names: List of feature names
        cv_folds: Number of cross-validation folds
        save_dir: Directory to save trained models (optional)
        
    Returns:
        Dictionary mapping model names to their results
    """
    model_names = ['RandomForest', 'GradientBoosting', 'LogisticRegression', 'SVM']
    results = {}
    
    logger.info("=" * 60)
    logger.info("Training Baseline Models")
    logger.info("=" * 60)
    
    for name in model_names:
        logger.info(f"\n{'─' * 40}")
        logger.info(f"Model: {name}")
        logger.info(f"{'─' * 40}")
        
        # Train
        model, cv_scores = train_baseline(name, X_train, y_train, cv_folds)
        
        # Evaluate
        metrics = evaluate_model(model, X_test, y_test, name)
        
        # Feature importance
        importance_df = get_feature_importance(model, feature_names, name)
        
        results[name] = {
            'model': model,
            'metrics': metrics,
            'cv_scores': cv_scores,
            'feature_importance': importance_df,
        }
        
        # Save model
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)
            model_path = os.path.join(save_dir, f'{name.lower()}_model.joblib')
            joblib.dump(model, model_path)
            logger.info(f"  Model saved to: {model_path}")
    
    # Print comparison table
    logger.info(f"\n{'=' * 70}")
    logger.info("BASELINE MODEL COMPARISON")
    logger.info(f"{'=' * 70}")
    header = f"{'Model':<25s} {'Accuracy':>10s} {'Precision':>10s} {'Recall':>10s} {'F1':>10s}"
    logger.info(header)
    logger.info("-" * 70)
    
    for name, result in results.items():
        m = result['metrics']
        row = (
            f"{name:<25s} {m['accuracy']:>10.4f} {m['precision']:>10.4f} "
            f"{m['recall']:>10.4f} {m['f1_score']:>10.4f}"
        )
        logger.info(row)
    
    logger.info("=" * 70)
    
    return results


def load_model(model_path: str) -> Pipeline:
    """
    Load a saved model from disk.
    
    Args:
        model_path: Path to the saved model file
        
    Returns:
        Loaded model pipeline
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    
    model = joblib.load(model_path)
    logger.info(f"Model loaded from: {model_path}")
    return model
