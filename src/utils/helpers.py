"""
Utility Functions for the Phishing Domain Detection System.

Provides cross-cutting helpers used across the pipeline:
- ``setup_logging`` – configure file + console logging.
- ``load_config`` – read YAML configuration files.
- ``ensure_dir`` – create directories idempotently.
- ``Timer`` – context manager for wall-clock timing.
- ``format_results`` – pretty-print evaluation metrics as a table string.
- ``calculate_metrics`` – compute comprehensive classification metrics.
"""

import logging
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Optional, Union

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(
    log_file: Optional[str] = "logs/phishing_detection.log",
    level: int = logging.INFO,
    fmt: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
) -> logging.Logger:
    """Configure the root logger with console and (optionally) file handlers.

    Args:
        log_file: Path to the log file.  Pass ``None`` to disable file
            logging.
        level: Logging level (e.g. ``logging.DEBUG``).
        fmt: Log message format string.

    Returns:
        The configured root ``Logger`` instance.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid adding duplicate handlers on repeated calls
    if root_logger.handlers:
        return root_logger

    formatter = logging.Formatter(fmt)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    # File handler
    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(path), encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    root_logger.info("Logging initialised (level=%s, file=%s)", level, log_file)
    return root_logger


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load a YAML configuration file.

    Args:
        config_path: Path to the YAML file.

    Returns:
        Parsed configuration as a nested dictionary.

    Raises:
        FileNotFoundError: If *config_path* does not exist.
    """
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        raise ImportError(
            "PyYAML is required to load config files.  "
            "Install it with: pip install pyyaml"
        )

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path.resolve()}")

    with open(path, "r", encoding="utf-8") as fh:
        config: Dict[str, Any] = yaml.safe_load(fh) or {}

    logging.getLogger(__name__).info("Config loaded from %s", path.resolve())
    return config


# ---------------------------------------------------------------------------
# Filesystem
# ---------------------------------------------------------------------------

def ensure_dir(directory: Union[str, Path]) -> Path:
    """Create *directory* (and parents) if it does not already exist.

    Args:
        directory: Path string or ``Path`` object.

    Returns:
        The resolved ``Path``.
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


# ---------------------------------------------------------------------------
# Timer
# ---------------------------------------------------------------------------

class Timer:
    """Context manager that measures elapsed wall-clock time.

    Usage::

        with Timer("Training") as t:
            train_model()
        print(t.elapsed)  # seconds as float

    It also works as a decorator-less object::

        t = Timer("Inference")
        t.start()
        run_inference()
        t.stop()
        print(t.elapsed)
    """

    def __init__(self, name: str = "Timer") -> None:
        self.name = name
        self.elapsed: float = 0.0
        self._start: float = 0.0
        self._logger = logging.getLogger(__name__)

    def start(self) -> "Timer":
        """Start (or restart) the timer."""
        self._start = time.perf_counter()
        return self

    def stop(self) -> float:
        """Stop the timer and return elapsed seconds."""
        self.elapsed = time.perf_counter() - self._start
        self._logger.info("%s finished in %.4f s", self.name, self.elapsed)
        return self.elapsed

    def __enter__(self) -> "Timer":
        self.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.stop()


# ---------------------------------------------------------------------------
# Results formatting
# ---------------------------------------------------------------------------

def format_results(
    results: Dict[str, Dict[str, float]],
    title: str = "Model Comparison",
) -> str:
    """Format evaluation results as a human-readable table string.

    Args:
        results: Mapping of ``{model_name: {metric: value, …}, …}``.
        title: Table title.

    Returns:
        Multi-line formatted table string.
    """
    if not results:
        return "No results to display."

    # Collect all metric names
    all_metrics = sorted(
        {m for metrics in results.values() for m in metrics}
    )

    # Column widths
    name_w = max(len(name) for name in results) + 2
    col_w = max(max(len(m) for m in all_metrics) + 2, 10)

    # Header
    header = f"{'Model':<{name_w}}" + "".join(
        f"{m:>{col_w}}" for m in all_metrics
    )
    sep = "─" * len(header)

    lines = [
        "",
        f"  {title}",
        f"  {sep}",
        f"  {header}",
        f"  {sep}",
    ]

    for name, metrics in results.items():
        row = f"{name:<{name_w}}"
        for m in all_metrics:
            val = metrics.get(m, 0.0)
            row += f"{val:>{col_w}.4f}"
        lines.append(f"  {row}")

    lines.append(f"  {sep}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def calculate_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
    class_names: Optional[list] = None,
) -> Dict[str, Any]:
    """Compute comprehensive classification metrics.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        y_prob: Predicted probabilities for the positive class (optional).
        class_names: Names for each class (default ``["legit", "phishing"]``).

    Returns:
        Dictionary containing scalar metrics, confusion matrix, and the
        full classification report string.
    """
    if class_names is None:
        class_names = ["legit", "phishing"]

    metrics: Dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, y_pred)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(
            y_true, y_pred, target_names=class_names, zero_division=0,
        ),
    }

    if y_prob is not None:
        try:
            metrics["auc_roc"] = float(roc_auc_score(y_true, y_prob))
            fpr, tpr, _ = roc_curve(y_true, y_prob)
            metrics["roc_curve"] = {"fpr": fpr.tolist(), "tpr": tpr.tolist()}
            prec_arr, rec_arr, _ = precision_recall_curve(y_true, y_prob)
            metrics["pr_curve"] = {
                "precision": prec_arr.tolist(),
                "recall": rec_arr.tolist(),
            }
        except ValueError:
            metrics["auc_roc"] = 0.0

    return metrics
