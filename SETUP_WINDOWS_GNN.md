# Windows GNN Environment Setup (Python 3.11)

Because DGL (Deep Graph Library) requires compiled C++ binaries that are currently unavailable for futuristic Python versions like Python 3.14, executing the Relational Graph Convolutional Network (RGCN) on Windows natively requires a strictly controlled **Python 3.11** environment.

Follow these exact PowerShell commands to initialize the environment, install the correct PyTorch and DGL wheels, and verify the GNN pipeline.

## 1. Install Prerequisites

Ensure you have the Microsoft Visual C++ Redistributable installed. This is required for DGL's underlying C++ execution engine:

```powershell
winget install --id Microsoft.VCRedist.2015+.x64 --exact
```

Ensure you have Python 3.11 installed. You can install it via winget:

```powershell
winget install --id Python.Python.3.11 --exact
```

## 2. Create and Activate the Virtual Environment

Open PowerShell, navigate to the `phishing-domain-detection` project root, and execute:

```powershell
# Create the environment using Python 3.11
py -3.11 -m venv .venv-gnn

# Activate the environment
.\.venv-gnn\Scripts\Activate.ps1
```

*(Note: If you receive a script execution error, run `Set-ExecutionPolicy Unrestricted -Scope CurrentUser` first).*

## 3. Install Dependencies

With the `.venv-gnn` active, install the strictly pinned requirements file. This file contains the custom wheel links required for PyTorch and DGL to install properly on Windows.

```powershell
python -m pip install --upgrade pip
pip install -r requirements-gnn.txt
```

## 4. Verify the Installation

Ensure that DGL and PyTorch successfully imported without throwing DLL errors:

```powershell
python -c "import torch, dgl, networkx, sklearn; print('PyTorch:', torch.__version__); print('DGL:', dgl.__version__); print('Setup Successful!')"
```

## 5. End-to-End Verification

Finally, run the custom GNN verification script to build the graph, train the native DGL RGCN model, and evaluate its metrics:

```powershell
python verify_gnn.py
```

If successful, the script will output `MODEL_MODE: DGL_RGCN` and display the final accuracy metrics!
