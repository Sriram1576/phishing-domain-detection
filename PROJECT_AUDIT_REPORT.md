# Project Audit Report

**Project:** PhishNet-GNN — Real-Time Phishing Domain Detection via Graph Neural Networks  
**Audit Date:** 2026-09-02  
**Auditor:** QA Engineer / ML Project Auditor  
**Required Stack:** NetworkX, DGL (Deep Graph Library), Scikit-Learn

---

## Overall Verdict

### ⚠️ PARTIAL PASS

> The DGL/RGCN architecture **is correctly implemented in code** — the heterogeneous graph construction, PhishRGCN model with HeteroGraphConv layers, Focal Loss, and full training pipeline are all present and well-structured. However, the DGL/RGCN **did NOT successfully execute** in this environment due to a Python version incompatibility (Python 3.14 vs. DGL's requirement for Python ≤ 3.12) and a critical DLL load failure. Additionally, several code-level bugs were found that would prevent correct execution even in a compatible environment.

---

## Requirement Checklist

| # | Requirement | Implemented in Code | Successfully Executed | Evidence / File / Output | Status |
|---|------------|:------------------:|:--------------------:|--------------------------|--------|
| 1 | NetworkX used for graph construction | ✅ Yes | ❌ Not tested (DGL blocked) | `graph_builder.py` L3: `import networkx as nx`, L23: `self.graph = nx.Graph()`, L59: `self.graph.add_node(...)`, L74/87: `self.graph.add_edge(...)` | ✅ PASS (code) |
| 2 | DGL used for heterogeneous graph | ✅ Yes | ❌ DLL load failure | `graph_builder.py` L10: `import dgl`, L152: `dgl.heterograph(graph_data, num_nodes_dict=...)` | ⚠️ PARTIAL |
| 3 | Canonical edge types present | ✅ Yes | ❌ Not executed | `graph_builder.py` L131–143: All 5 canonical edge types defined: `('domain','has_ip','ip')`, `('ip','ip_of','domain')`, `('domain','has_ns','nameserver')`, `('nameserver','ns_of','domain')`, `('domain','self','domain')` | ✅ PASS (code) |
| 4 | Real DGL GNN (HeteroGraphConv/RGCN) | ✅ Yes | ❌ DGL import failed | `gnn_model.py` L12: `import dgl.nn as dglnn`, L45–48: `dglnn.HeteroGraphConv({rel: dglnn.GraphConv(...)})` with 5 relation types | ✅ PASS (code) |
| 5 | Domain features at `g.nodes['domain'].data['feat']` | ✅ Yes | ❌ Not executed | `graph_builder.py` L156: `g.nodes['domain'].data['feat'] = torch.tensor(domain_features, ...)` | ✅ PASS (code) |
| 6 | 21 real lexical/DNS features (not random) | ✅ Yes | ❌ Not tested | `feature_extractor.py` L399–407: `get_feature_names()` returns exactly 21 named features (17 lexical + 4 DNS-aware). All computed from real domain properties. | ✅ PASS (code) |
| 7 | GNN input dimension reads from tensor | ✅ Yes | ❌ Not executed | `trainer.py` L276–279: `in_feats[ntype] = g.nodes[ntype].data['feat'].shape[1]` — dynamically reads feature tensor dimension | ✅ PASS (code) |
| 8 | 80/10/10 (or equivalent) train/val/test split | ✅ Yes (70/15/15 in config) | ❌ Not executed | `trainer.py` L55–57: reads `train_ratio`, `val_ratio`, `test_ratio` from config; `config.yaml` L120–122: `0.7 / 0.15 / 0.15` | ✅ PASS (code) |
| 9 | Focal Loss for class imbalance | ✅ Yes | ❌ Not executed | `gnn_model.py` L80–98: `FocalLoss` class (alpha=0.25, gamma=2.0); `trainer.py` L292–296: selected when config `loss.type == 'focal'`; `config.yaml` L112: `type: "focal"` | ✅ PASS (code) |
| 10 | Scikit-Learn for baselines and metrics | ✅ Yes | ❌ Not tested | `baseline.py`: RandomForest, GradientBoosting, LogisticRegression, SVM with GridSearchCV; `trainer.py` L363: sklearn.metrics for GNN evaluation | ✅ PASS (code) |
| 11 | Full evaluation metrics suite | ✅ Yes | ❌ Not executed | `trainer.py` L363–376: Accuracy, Precision, Recall, F1, ROC-AUC; `baseline.py` L178–196: same + Confusion Matrix; `verify_gnn.py` L107: confusion_matrix | ✅ PASS (code) |
| 12 | Saves/loads GNN weights | ✅ Yes (but path discrepancy) | ✅ File exists (1,071,861 bytes) | `trainer.py` L308: saves to `models/saved/phish_rgcn.pt`; `predict.py` L137: **loads from `saved_models/phish_rgcn.pt`** — MISMATCH | ⚠️ PARTIAL |
| 13 | Inference outputs `MODEL_MODE: DGL_RGCN` | ✅ Yes (code present) | ❌ Observed: `SKLEARN_FALLBACK` | `predict.py` L66: `print("MODEL_MODE: DGL_RGCN")` — but DGL import fails, so L76: `print("MODEL_MODE: SKLEARN_FALLBACK")` is reached | ❌ FAIL (runtime) |

---

## Environment Details

| Property | Value |
|----------|-------|
| **Operating System** | Windows (AMD64) |
| **Python Version** | 3.14.5 (MSC v.1944 64-bit) |
| **Python Executable** | `C:\Users\subha\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| **Virtual Environment** | ❌ **NONE ACTIVE** (`sys.prefix == sys.base_prefix`). No `.venv-gnn` or `venv` directory found. |
| **Required Python** | 3.10 or 3.11 (per requirements-gnn.txt and SETUP_WINDOWS_GNN.md) |

### Dependency Version Comparison

| Package | Required (requirements-gnn.txt) | Installed | Match | Notes |
|---------|--------------------------------|-----------|:-----:|-------|
| numpy | 1.26.4 | 2.5.1 | ❌ | Major version mismatch |
| pandas | 2.2.1 | 3.0.3 | ❌ | Major version mismatch |
| scikit-learn | 1.4.1.post1 | 1.9.0 | ❌ | Minor version mismatch |
| dnspython | 2.6.1 | 2.8.0 | ❌ | Minor version mismatch |
| tldextract | 5.1.2 | 5.3.2 | ❌ | Minor version mismatch |
| Levenshtein | 0.25.0 | 0.27.3 | ❌ | Minor version mismatch |
| networkx | 3.2.1 | 3.6.1 | ❌ | Minor version mismatch |
| torch | 2.2.1+cpu | 2.13.0+cpu | ❌ | Major version mismatch |
| torchaudio | 2.2.1+cpu | Not checked | ❌ | — |
| torchvision | 0.17.1+cpu | Not checked | ❌ | — |
| dgl | 2.1.0 | 0.1.3 | ❌ | **CRITICAL: Major version mismatch** (0.1.3 vs 2.1.0) |
| flask | 3.0.2 | 3.1.3 | ❌ | Minor version mismatch |
| flask-cors | 4.0.0 | 6.0.5 | ❌ | Major version mismatch |
| waitress | 3.0.0 | Not detected | ❌ | — |

> **⚠️ CRITICAL:** Not a single installed package version matches requirements-gnn.txt. The environment is a Python 3.14 system install with incompatible packages, not the required Python 3.11 virtual environment.

---

## Graph and Model Evidence

| Property | Evidence |
|----------|---------|
| **NetworkX Usage** | `graph_builder.py`: `nx.Graph()` creates the base graph; `add_node()` and `add_edge()` for domain/IP/NS nodes and edges; `nx.density()` for stats |
| **DGL Graph Type** | `dgl.heterograph()` — heterogeneous graph with `num_nodes_dict` |
| **Node Types** | `domain`, `ip`, `nameserver` (3 types) |
| **Canonical Edge Types** | `('domain','has_ip','ip')`, `('ip','ip_of','domain')`, `('domain','has_ns','nameserver')`, `('nameserver','ns_of','domain')`, `('domain','self','domain')` — all 5 present with bidirectional relations |
| **Domain Feature Tensor** | `g.nodes['domain'].data['feat']` shape expected: `[N, 21]` |
| **Feature Count & Names** | 21 features: `domain_length`, `subdomain_count`, `dot_count`, `hyphen_count`, `digit_count`, `special_char_count`, `entropy`, `has_ip`, `vowel_ratio`, `digit_ratio`, `is_punycode`, `tld_length`, `longest_word_length`, `suspicious_tld`, `brand_similarity`, `consonant_sequence`, `contains_login_keywords`, `num_a_records`, `num_ns_records`, `dns_resolved`, `dns_failed` |
| **GNN Architecture** | `PhishRGCN`: 3-layer HeteroGraphConv with per-relation GraphConv, BatchNorm, ReLU, Dropout(0.3), followed by 2-layer MLP classifier |
| **Loss Function** | `FocalLoss(alpha=0.25, gamma=2.0)` configured in `config.yaml` |
| **Dataset Split** | 70% train / 15% val / 15% test (from config.yaml) |
| **Saved Model** | `models/saved/phish_rgcn.pt` — EXISTS (1,071,861 bytes) |

---

## Execution Results

### Test 1: Dependency Import Test

```
Command: python -c "import sys, torch, dgl, networkx, sklearn; ..."
Exit Code: 1

ERROR:
FileNotFoundError: Could not find module
'C:\Users\subha\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\dgl\libdgl.dll'
(or one of its dependencies). Try using the full path with constructor syntax.
```

**Individual Results:**
- ✅ torch: 2.13.0+cpu (imports OK)
- ❌ dgl: FileNotFoundError on libdgl.dll (DLL load failure)
- ✅ networkx: 3.6.1 (imports OK)
- ✅ sklearn: 1.9.0 (imports OK)
- ✅ numpy: 2.5.1 (imports OK)
- ✅ pandas: 3.0.3 (imports OK)
- ✅ dnspython: imports OK
- ✅ tldextract: imports OK

**Note:** `libdgl.dll` file physically exists on disk, but it (or one of its C++ runtime dependencies) cannot be loaded by Python 3.14's `ctypes.CDLL`. This is a binary compatibility failure — the DGL 0.1.3 wheel was not compiled for Python 3.14.

### Test 2: verify_gnn.py

```
Command: python verify_gnn.py
Exit Code: 1

Output:
============================================================
VERIFYING DGL & PYTORCH ENVIRONMENT
============================================================
Traceback (most recent call last):
  ...
  File "dgl\_ffi\base.py", line 35, in _load_lib
    lib = ctypes.CDLL(lib_path[0], ctypes.RTLD_GLOBAL)
FileNotFoundError: Could not find module '...\dgl\libdgl.dll'
(or one of its dependencies).
```

**Script halted at the first verification step. No graph was built, no model was trained, and no metrics were produced.**

### Test 3: Prediction Inference

```
Command: python src/predict.py --domain "https://google.com"
Exit Code: 0

Output (predict.py ignores --domain, runs hardcoded test_urls):
MODEL_MODE: SKLEARN_FALLBACK
[ URL ] http://paypal-verification-update.com.tk
   Probability  : 40.00%
   Verdict      : BENIGN
[ URL ] https://google.com
   Probability  : 0.00%
   Verdict      : BENIGN
```

**Note:** The script does not parse `--domain` CLI arguments. It always runs its hardcoded `test_urls` list from `__main__`. The output explicitly shows `MODEL_MODE: SKLEARN_FALLBACK` (heuristic scoring), NOT `DGL_RGCN`.

### Final Observed Model Mode: **SKLEARN_FALLBACK**

---

## Problems Found

### 🔴 Issue 1: Python Version Incompatibility (Critical)

| Field | Detail |
|-------|--------|
| **Issue** | Python 3.14 is incompatible with DGL |
| **Error** | `FileNotFoundError: Could not find module '...\dgl\libdgl.dll'` |
| **Cause** | DGL's C++ native library (`libdgl.dll`) was not compiled for Python 3.14. DGL 2.1.0 officially supports Python 3.8–3.12. The installed DGL 0.1.3 is an ancient version that also lacks 3.14 support. |
| **Affected** | Entire GNN pipeline — `dgl` cannot be imported at all |
| **Severity** | 🔴 **Critical** |
| **Fix** | Create a Python 3.11 virtual environment as per `SETUP_WINDOWS_GNN.md`: `py -3.11 -m venv .venv-gnn` and install `requirements-gnn.txt` |

---

### 🔴 Issue 2: No Virtual Environment Active (Critical)

| Field | Detail |
|-------|--------|
| **Issue** | No virtual environment is active or even present |
| **Error** | `sys.prefix == sys.base_prefix` (system Python); `.venv-gnn` and `venv` directories do not exist |
| **Cause** | The environment setup in `SETUP_WINDOWS_GNN.md` was never executed |
| **Affected** | All dependency version pinning; isolation from system packages |
| **Severity** | 🔴 **Critical** |
| **Fix** | Follow the exact steps in `SETUP_WINDOWS_GNN.md` to create `.venv-gnn` |

---

### 🔴 Issue 3: DGL Version Mismatch — 0.1.3 vs 2.1.0 (Critical)

| Field | Detail |
|-------|--------|
| **Issue** | Installed DGL version is 0.1.3; required is 2.1.0 |
| **Error** | DGL 0.1.3 does not have `dgl.heterograph`, `dgl.nn.HeteroGraphConv`, or any of the modern APIs used by this project |
| **Cause** | `pip install dgl` on Python 3.14 pulled an ancient fallback wheel instead of the correct 2.1.0 build |
| **Affected** | `graph_builder.py`, `gnn_model.py`, `trainer.py`, `predict.py`, `verify_gnn.py` |
| **Severity** | 🔴 **Critical** |
| **Fix** | In a Python 3.11 venv, install with: `pip install dgl==2.1.0 --find-links https://data.dgl.ai/wheels/repo.html` |

---

### 🔴 Issue 4: Edge Attribute Key Mismatch in graph_builder.py (Critical)

| Field | Detail |
|-------|--------|
| **Issue** | NetworkX edges are stored with `type='has_ip'` but read back with `data.get('relation')` |
| **Error** | No edges are extracted during DGL conversion — all edge lists remain empty |
| **Cause** | `build_graph()` at L74/L87 uses `type='has_ip'` and `type='has_ns'`. But `to_dgl_graph()` at L122 reads `data.get('relation')` instead of `data.get('type')`. The key `'relation'` is never set; `'type'` is. |
| **Affected** | `src/graph/graph_builder.py` L121–128 |
| **Severity** | 🔴 **Critical** — The DGL heterograph will have **zero has_ip and has_ns edges** (only self-loops). The GNN degenerates into an MLP because no cross-type message passing occurs. |
| **Fix** | Change L122 from `data.get('relation')` to `data.get('type')`, or change L74/L87 to use `relation='has_ip'`/`relation='has_ns'` |

---

### 🟠 Issue 5: Model Path Mismatch in predict.py (High)

| Field | Detail |
|-------|--------|
| **Issue** | `predict.py` loads model from `saved_models/phish_rgcn.pt` but model is saved at `models/saved/phish_rgcn.pt` |
| **Error** | `FileNotFoundError` when GNN forward pass attempts to load weights |
| **Cause** | `predict.py` L137: `PROJECT_ROOT / "saved_models" / "phish_rgcn.pt"` vs `config.yaml` L138: `models_dir: "models/saved/"` and `trainer.py` L308 which saves there |
| **Affected** | `src/predict.py` L137 |
| **Severity** | 🟠 **High** — GNN inference will always fail and fall back to heuristic scoring, even if DGL is working |
| **Fix** | Change L137 to `PROJECT_ROOT / "models" / "saved" / "phish_rgcn.pt"` |

---

### 🟠 Issue 6: verify_gnn.py Imports Non-Existent Function (High)

| Field | Detail |
|-------|--------|
| **Issue** | `verify_gnn.py` L119 imports `from src.predict import predict_domain` but the function is named `predict_url` |
| **Error** | `ImportError: cannot import name 'predict_domain' from 'src.predict'` |
| **Cause** | Function was renamed from `predict_domain` to `predict_url` but verify script was not updated |
| **Affected** | `verify_gnn.py` L119 |
| **Severity** | 🟠 **High** — The inference verification step in verify_gnn.py will always crash |
| **Fix** | Change L119 to `from src.predict import predict_url as predict_domain` or update all references |

---

### 🟠 Issue 7: verify_gnn.py References Missing CSV Files (High)

| Field | Detail |
|-------|--------|
| **Issue** | `verify_gnn.py` loads `data/dns_dataset.csv` and `data/features_dataset.csv` which do not exist |
| **Error** | `FileNotFoundError` at L47–48 |
| **Cause** | The trainer pipeline (`trainer.py`) resolves DNS and extracts features on-the-fly and never saves them as separate CSVs. The verify script assumes pre-generated files. |
| **Affected** | `verify_gnn.py` L47–48 |
| **Severity** | 🟠 **High** — `verify_pipeline()` will fail even if DGL is fixed |
| **Fix** | Either generate these CSVs during training, or modify verify_gnn.py to use the trainer pipeline methods |

---

### 🟠 Issue 8: predict.py Ignores CLI Arguments (High)

| Field | Detail |
|-------|--------|
| **Issue** | `python src/predict.py --domain "https://google.com"` does not parse `--domain`; runs hardcoded test URLs |
| **Error** | No error — silently ignores the argument |
| **Cause** | `predict.py` has no `argparse` or `sys.argv` handling; `__main__` block uses hardcoded `test_urls` list |
| **Affected** | `src/predict.py` L204–222 |
| **Severity** | 🟠 **High** — User cannot test arbitrary domains from CLI |
| **Fix** | Add `argparse` with `--domain` argument, falling back to test URLs if none provided |

---

### 🟡 Issue 9: Every Installed Package Version Mismatches (Medium)

| Field | Detail |
|-------|--------|
| **Issue** | All 12+ packages deviate from requirements-gnn.txt pinned versions |
| **Error** | No direct error, but API incompatibilities may exist |
| **Cause** | System Python 3.14 has latest package versions instead of the pinned versions |
| **Affected** | Entire project |
| **Severity** | 🟡 **Medium** — Once the Python 3.11 venv is created, `pip install -r requirements-gnn.txt` will fix this |
| **Fix** | Create the proper virtual environment |

---

### 🟡 Issue 10: Config train_ratio=0.7 But Audit Expected 0.8 (Medium)

| Field | Detail |
|-------|--------|
| **Issue** | Config specifies 70/15/15 split instead of the audit's expected 80/10/10 |
| **Error** | None — this is a design decision, not a bug |
| **Cause** | `config.yaml` L120–122: `train_ratio: 0.7, val_ratio: 0.15, test_ratio: 0.15` |
| **Affected** | `config.yaml`, `trainer.py` |
| **Severity** | 🟡 **Medium** — The split is reasonable and correctly implemented; just different from the audit's expected default |
| **Fix** | None needed unless 80/10/10 is a hard requirement |

---

### 🟢 Issue 11: Confusion Matrix Not Returned from train_rgcn (Low)

| Field | Detail |
|-------|--------|
| **Issue** | `trainer.py`'s `train_rgcn()` returns accuracy, precision, recall, F1, ROC-AUC but not the confusion matrix |
| **Error** | None — verify_gnn.py works around this by re-evaluating |
| **Cause** | Intentional omission; confusion matrix is computed separately in verify_gnn.py |
| **Affected** | `trainer.py` L370–376 |
| **Severity** | 🟢 **Low** — Metrics are still available via sklearn |
| **Fix** | Add confusion_matrix to `test_metrics` dict |

---

### 🟢 Issue 12: predict.py Zeros Out Features for Background Domains (Low)

| Field | Detail |
|-------|--------|
| **Issue** | During GNN inference, `predict.py` rebuilds the full graph but sets all background domain features to 0.0 |
| **Error** | Degraded model accuracy during inference |
| **Cause** | `predict.py` L118–119: `features_df[col] = 0.0` for all domains except the target |
| **Affected** | `src/predict.py` L116–125 |
| **Severity** | 🟢 **Low** — This is a known simplification (documented in comment at L110–111). In production, precomputed features would be loaded. |
| **Fix** | Save and load the precomputed feature matrix from training |

---

## Final Next Action

**The single most important next action is:**

```powershell
# 1. Install Python 3.11 if not present
winget install --id Python.Python.3.11 --exact

# 2. Create the required virtual environment
py -3.11 -m venv .venv-gnn

# 3. Activate it
.\.venv-gnn\Scripts\Activate.ps1

# 4. Install pinned dependencies
python -m pip install --upgrade pip
pip install -r requirements-gnn.txt

# 5. Verify DGL loads
python -c "import dgl; print('DGL:', dgl.__version__)"
```

After the environment is fixed, the **edge attribute key bug** (`'relation'` vs `'type'`) in `graph_builder.py` L122 must be fixed before the GNN can produce meaningful results.

---

## Summary

| Metric | Count |
|--------|-------|
| **Overall Verdict** | ⚠️ **PARTIAL PASS** |
| 🔴 Critical Issues | **4** |
| 🟠 High Issues | **4** |
| 🟡 Medium Issues | **2** |
| 🟢 Low Issues | **2** |
| **Total Issues** | **12** |

**Report Path:** `d:\Business\phishing-domain-detection\PROJECT_AUDIT_REPORT.md`

---

> 📋 **Please share this report with your mentor or AI assistant for review.** The architecture is sound and well-designed, but the environment must be set up correctly (Python 3.11 + pinned DGL 2.1.0) and the edge attribute key bug must be fixed before the true DGL_RGCN mode can execute successfully.
