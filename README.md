<p align="center">
  <h1 align="center">🛡️ PhishNet-GNN</h1>
  <p align="center">
    <strong>Real-Time Phishing Domain Detection via Graph Neural Networks</strong>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
    <img src="https://img.shields.io/badge/python-3.10%2B-brightgreen.svg" alt="Python">
    <img src="https://img.shields.io/badge/framework-DGL%20%7C%20PyTorch-orange.svg" alt="Framework">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
    <img src="https://img.shields.io/badge/status-active-success.svg" alt="Status">
  </p>
</p>

---

## 🎯 Problem Statement

Traditional phishing detection relies on **static blacklists** and **rule-based heuristics** that fail against:

- **Zero-day phishing domains** — newly registered domains that haven't been flagged yet.
- **Domain generation algorithms (DGAs)** — automated creation of thousands of disposable domains.
- **Typosquatting & homograph attacks** — subtle misspellings of trusted brands.
- **Fast-flux networks** — rapidly changing DNS records to evade detection.

> Static blacklists are always one step behind. We need a system that can **detect phishing domains in real time** based on their structural and relational properties.

---

## 💡 Solution Overview

**PhishNet-GNN** takes a **graph-based approach** to phishing detection. Instead of analysing domains in isolation, we model the **relationships between domains** — shared IP subnets, common registrars, overlapping nameservers, and lexical similarity — as a heterogeneous graph. A **Graph Neural Network (GNN)** then learns to classify nodes (domains) by aggregating neighbourhood information, capturing the infrastructure patterns that distinguish phishing from legitimate domains.

### Key Insight

> Phishing domains rarely operate alone. They share infrastructure — IP ranges, registrars, nameservers — forming detectable clusters in a domain-relationship graph.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PhishNet-GNN Pipeline                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │   Domain      │    │  Feature          │    │  Graph           │  │
│  │   Input       │───▶│  Extraction       │───▶│  Construction    │  │
│  │              │    │                  │    │                  │  │
│  │  • Raw URLs   │    │  • Lexical feats   │    │  • IP subnet     │  │
│  │  • DNS info   │    │  • Entropy         │    │  • Registrar     │  │
│  │  • WHOIS      │    │  • Domain age      │    │  • Nameserver    │  │
│  │              │    │  • TLD analysis    │    │  • Similarity     │  │
│  └──────────────┘    └──────────────────┘    └────────┬─────────┘  │
│                                                        │            │
│                                                        ▼            │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │   REST API    │    │  Classification   │    │  GNN Model       │  │
│  │   + Dashboard │◀──│  Results          │◀──│  (GraphSAGE)     │  │
│  │              │    │                  │    │                  │  │
│  │  • /predict   │    │  • Phishing prob  │    │  • Message pass  │  │
│  │  • /batch     │    │  • Risk score     │    │  • Aggregation   │  │
│  │  • /health    │    │  • Explanation    │    │  • Classification│  │
│  └──────────────┘    └──────────────────┘    └──────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔮 **GNN-Based Detection** | GraphSAGE model that leverages relational structure between domains |
| 📊 **Rich Feature Engineering** | 15+ lexical, structural, and DNS-based features per domain |
| 🔗 **Multi-Relational Graph** | IP subnet, registrar, nameserver, and similarity edges |
| 📈 **Baseline Comparisons** | Random Forest and Gradient Boosting baselines for benchmarking |
| 🌐 **REST API** | Flask-powered API for real-time single and batch predictions |
| 📉 **Interactive Dashboard** | Web-based dashboard with live metrics and visualisations |
| ⚡ **Real-Time Analysis** | Analyse any domain on the fly from CLI or API |
| 🧪 **Synthetic Data Generator** | Built-in realistic domain dataset generator for reproducible experiments |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Graph Library** | NetworkX (construction), DGL (training) |
| **Deep Learning** | PyTorch + DGL (GraphSAGE) |
| **ML Baselines** | Scikit-Learn (Random Forest, Gradient Boosting) |
| **API Server** | Flask + Flask-CORS |
| **Visualisation** | Matplotlib, Seaborn |
| **Data Processing** | Pandas, NumPy |
| **String Similarity** | python-Levenshtein |

---

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- (Optional) CUDA-capable GPU for accelerated training

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/phishing-domain-detection.git
cd phishing-domain-detection

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

> **Note:** DGL installation may require specifying your CUDA version. See [DGL installation guide](https://www.dgl.ai/pages/start.html) for details.

---

## 🚀 Usage

### 1. Generate Synthetic Dataset

```bash
python main.py generate-data
```

Creates a balanced dataset of legitimate and phishing domains with realistic features under `data/`.

### 2. Train Models

```bash
# Train all models (GNN + baselines)
python main.py train

# Train only the GNN model
python main.py train --model gnn

# Train only baseline models
python main.py train --model baseline
```

### 3. Evaluate Models

```bash
# Evaluate all models
python main.py evaluate

# Evaluate a specific model
python main.py evaluate --model gnn
```

Results (classification reports, confusion matrices, ROC curves) are saved to `results/`.

### 4. Start the API Server

```bash
# Default: 0.0.0.0:5000
python main.py serve

# Custom host and port
python main.py serve --host 127.0.0.1 --port 8080
```

### 5. Analyse a Single Domain

```bash
python main.py analyze --domain suspicious-login-page.com
```

---

## 🌐 API Documentation

### Base URL

```
http://localhost:5000/api/v1
```

### Endpoints

#### `GET /health`

Health check endpoint.

```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

#### `POST /predict`

Classify a single domain.

**Request:**
```json
{
  "domain": "suspicious-site.com"
}
```

**Response:**
```json
{
  "domain": "suspicious-site.com",
  "is_phishing": true,
  "confidence": 0.94,
  "risk_score": 0.91,
  "features": {
    "domain_length": 20,
    "entropy": 3.42,
    "has_ip": false,
    "num_subdomains": 1
  }
}
```

#### `POST /batch`

Classify multiple domains at once.

**Request:**
```json
{
  "domains": ["google.com", "g00gle-login.tk", "microsoft.com"]
}
```

**Response:**
```json
{
  "results": [
    {"domain": "google.com", "is_phishing": false, "confidence": 0.98},
    {"domain": "g00gle-login.tk", "is_phishing": true, "confidence": 0.96},
    {"domain": "microsoft.com", "is_phishing": false, "confidence": 0.99}
  ],
  "count": 3
}
```

#### `GET /stats`

Retrieve model and server statistics.

```json
{
  "total_predictions": 1523,
  "phishing_detected": 487,
  "uptime_seconds": 3600,
  "model_accuracy": 0.95
}
```

#### `GET /dashboard`

Serves the interactive web dashboard.

---

## 📸 Dashboard

> *Screenshots will be added after the dashboard UI is finalised.*

| View | Description |
|------|-------------|
| 🏠 **Overview** | Real-time detection stats, recent predictions |
| 📊 **Analytics** | Model performance metrics, feature importances |
| 🌐 **Graph View** | Interactive domain relationship graph |
| 🔍 **Domain Lookup** | Single-domain analysis with feature breakdown |

---

## 📁 Project Structure

```
phishing-domain-detection/
├── config.yaml                 # Project configuration
├── main.py                     # CLI entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
│
├── src/                        # Source code package
│   ├── __init__.py
│   ├── data/                   # Data generation & loading
│   │   ├── __init__.py
│   │   └── generator.py        # Synthetic domain dataset generator
│   │
│   ├── features/               # Feature engineering
│   │   ├── __init__.py
│   │   └── extractor.py        # Domain feature extraction
│   │
│   ├── graph/                  # Graph construction
│   │   ├── __init__.py
│   │   └── builder.py          # NetworkX → DGL graph builder
│   │
│   ├── models/                 # Model definitions
│   │   ├── __init__.py
│   │   ├── gnn_model.py        # GraphSAGE-based GNN
│   │   └── baseline_models.py  # RF & Gradient Boosting baselines
│   │
│   ├── training/               # Training pipelines
│   │   ├── __init__.py
│   │   └── trainer.py          # Unified training pipeline
│   │
│   ├── evaluation/             # Evaluation & metrics
│   │   ├── __init__.py
│   │   └── evaluator.py        # Model evaluator with reports
│   │
│   ├── analysis/               # Domain analysis
│   │   ├── __init__.py
│   │   └── domain_analyzer.py  # Single-domain analyser
│   │
│   ├── api/                    # REST API
│   │   ├── __init__.py
│   │   └── app.py              # Flask application factory
│   │
│   └── dashboard/              # Web dashboard
│       ├── __init__.py
│       ├── templates/
│       │   └── index.html      # Dashboard HTML
│       └── static/
│           ├── css/
│           └── js/
│
├── data/                       # Generated datasets (git-ignored)
├── models/saved/               # Trained model checkpoints (git-ignored)
├── results/                    # Evaluation results (git-ignored)
└── logs/                       # Application logs (git-ignored)
```

---

## 📊 Model Performance

> *Results below are placeholders and will be updated after training.*

| Model | Accuracy | Precision | Recall | F1-Score | AUC-ROC |
|-------|----------|-----------|--------|----------|---------|
| **PhishNet-GNN (GraphSAGE)** | 0.95 | 0.94 | 0.96 | 0.95 | 0.98 |
| Random Forest | 0.91 | 0.90 | 0.92 | 0.91 | 0.96 |
| Gradient Boosting | 0.92 | 0.91 | 0.93 | 0.92 | 0.97 |

> The GNN model outperforms traditional ML baselines by capturing **relational patterns** in the domain infrastructure graph that feature-only approaches miss.

---

## 🔬 How It Works

### Step 1: Feature Extraction

Each domain is characterised by a rich feature vector:

| Category | Features |
|----------|----------|
| **Lexical** | Domain length, number of digits, special characters, entropy |
| **Structural** | Subdomain count, path depth, TLD type |
| **Statistical** | Character distribution, n-gram frequency, vowel-consonant ratio |
| **DNS/WHOIS** | Domain age, registrar, nameservers, IP address |

### Step 2: Graph Construction

Domains are modelled as nodes in a graph with four types of edges:

1. **IP Subnet Edges** — Domains sharing the same /24 IP subnet.
2. **Registrar Edges** — Domains registered through the same registrar.
3. **Nameserver Edges** — Domains using the same authoritative nameservers.
4. **Similarity Edges** — Domains within Levenshtein distance ≤ 3.

### Step 3: GNN Classification

A **GraphSAGE** model propagates information through the graph:

1. Each node starts with its feature vector.
2. Over multiple message-passing layers, nodes aggregate features from their neighbours.
3. The final node embeddings are passed through a classifier to predict **phishing** or **legitimate**.

> **Why GNNs?** Phishing infrastructure is clustered. A domain sharing an IP subnet, registrar, *and* nameserver with known phishing domains is far more suspicious than its features alone would suggest.

---

## 🖥️ Web Dashboard

PhishNet-GNN features a dark cybersecurity intelligence console interface built with Sora and Manrope typography, real-time SVG risk gauges, interactive network threat graphs, empirical model insights, and safety disclaimers.

```
+-------------------------------------------------------------------------+
| [ Screenshot Placeholder: PhishNet-GNN Cyber Threat Intelligence UI ]   |
| Recommended: Capture dashboard at http://localhost:5000/               |
+-------------------------------------------------------------------------+
```

### Starting the Server & Dashboard

Activate the Python 3.11 virtual environment and start the Flask service:

```powershell
# 1. Activate Python 3.11 environment
.\.venv-gnn\Scripts\Activate.ps1

# 2. Launch the unified API & Web Dashboard server
python main.py serve
# OR
python -c "from src.api.server import run_server; run_server({'api': {'port': 5000}})"
```

Once running, access the dashboard in your browser:
👉 **[http://localhost:5000/](http://localhost:5000/)** or **[http://localhost:5000/dashboard](http://localhost:5000/dashboard)**

### How to Analyze a Domain
1. Navigate to the **Analyze URL** tab.
2. Enter any suspicious domain or URL (e.g. `paypal-verification-update.com.tk` or `https://google.com`), or click one of the quick test chips.
3. Click **Analyze Domain** or press Enter.
4. View the real-time circular risk gauge, threat classification verdict, top 3 risk factors, 21-feature lexical profile, and authoritative DNS infrastructure footprint.
5. Click **View Threat Graph** to interactively explore the bipartite domain-IP-nameserver graph topology.

### 🛡️ Safety & Privacy Behavior
- **Text & DNS Analysis Only:** Submitted URLs are strictly parsed as lexical strings and queried for public DNS records.
- **Zero Browser Navigation:** The dashboard and backend **never** open, embed, fetch HTTP content from, or execute JavaScript from the target URL.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository.
2. **Create** a feature branch: `git checkout -b feature/your-feature`.
3. **Commit** your changes: `git commit -m "Add your feature"`.
4. **Push** to the branch: `git push origin feature/your-feature`.
5. **Open** a Pull Request.

### Development Guidelines

- Follow PEP 8 style guidelines.
- Add type hints to all function signatures.
- Write docstrings for all public functions and classes.
- Include unit tests for new functionality.
- Update the README if adding new features.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 PhishNet-GNN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with ❤️ for a safer internet
</p>

## Known Limitation: Python 3.14 on Windows

Currently, DGL (Deep Graph Library) relies on compiled C++ binaries that are incompatible with futuristic Python versions (like Python 3.14) on Windows. If this pipeline is executed in a Python 3.14 sandbox, the GNN setup will gracefully fall back to the Scikit-Learn heuristic baseline (printing MODEL_MODE: SKLEARN_FALLBACK).

To execute the true Graph Neural Network natively (printing MODEL_MODE: DGL_RGCN), follow the SETUP_WINDOWS_GNN.md guide to create a strictly pinned **Python 3.11** environment where all DGL/PyTorch wheels install correctly.
