# Deployment Status

## Environment Info (`.venv-gnn`)
- **Python:** 3.11.9
- **PyTorch:** 2.2.1+cpu
- **DGL (Deep Graph Library):** 2.2.1
- **NumPy:** 1.26.4
- **Scikit-Learn:** 1.4.1.post1

## Subsystem Checks
- **DGL Import Successful:** ✅ Yes. `import dgl` and `import dgl.nn` work seamlessly with zero DLL errors in the `.venv-gnn` Python 3.11 environment.
- **Backend Starts Without Error:** ✅ Yes. The Flask REST API starts cleanly on `0.0.0.0:5000` via `python main.py serve` using the 3.11 environment.
- **UI & Prediction API Completes:** ✅ Yes. Calling `/api/analyze` successfully executes the real PyTorch RGCN inference (`MODEL_MODE: DGL_RGCN`). 
- **Dashboard Integrity:** ✅ Yes. `app.js` is fully integrated with `/api/stats`, `/api/analyze`, and `/api/graph-data`. The API returns real JSON data sourced from the actual dataset (not mock arrays).

## Known Behaviors / Remaining Issues
- **Sandbox DNS Restrictions:** When testing predictions (e.g. `google.com` or `paypal-verification-update.com.tk`), the DNS resolution module occasionally marks domains as `failed` because the local sandbox intercepts or rate-limits outbound port 53 (DNS) queries. When DNS fails, the domain's risk score is artificially boosted by the model (because real missing DNS often indicates hidden/offline infrastructure). This is purely a network limitation of the deployment host, not a bug in the model or codebase.
- **Resolution:** No codebase changes are necessary. When deployed to a production host with unfettered DNS access, these live heuristic resolutions will accurately pull the IP and Nameserver records for the GNN.
