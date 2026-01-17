<<<<<<< HEAD
## URL Phishing Detector
=======
## URL Phishing Detector – Phishing URL Detector
>>>>>>> 1d6ce02 (changed name)

AI-powered phishing / malicious URL classifier backed by a high-accuracy XGBoost model, exposed via a FastAPI backend and a minimal browser extension UI.

---

### Quick Start (All OS)

Prerequisites:

- Python 3.10 or newer (3.12 recommended)
- A Chromium-based browser (Chrome, Edge, Brave) for the extension

1) Create and activate a virtual environment

- Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

- Windows (Cmd):

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
```

- macOS/Linux (bash/zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Train the model (once)

```bash
python train_model.py
```

This trains an XGBoost model on `web-page-phishing.csv` and saves it to `model/phishing_model.joblib`.

4) Run the API server

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

5) Test the API

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Expected JSON includes `is_phishing` and `probability_phishing`.

6) Load the browser extension

1. Open Chrome/Edge and navigate to `chrome://extensions`.
2. Enable Developer mode.
3. Click "Load unpacked" and select the `extension` folder.

The extension reads the active tab URL, calls `http://localhost:8000/predict`, and shows a clear risk status.

---

### Notes & Troubleshooting

- If `Activate.ps1` is blocked on Windows PowerShell, temporarily relax policy for the session:

<<<<<<< HEAD
You can tweak `train_model.py` hyperparameters to push accuracy even higher if you benchmark on your own validation splits.
=======
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

- If `uvicorn` is not found, ensure the venv is active and reinstall requirements:

```bash
pip install -r requirements.txt
```

- If the extension shows an error reaching the API, confirm the server is running at `http://localhost:8000` and that your firewall allows local requests.

---

### Project Structure & How It Works

- `url_features.py`: URL structure feature extraction (length, counts of symbols, heuristic redirection count).
- `train_model.py`: Loads the dataset, trains a scaled numeric pipeline + XGBoost, saves the model bundle.
- `api.py`: FastAPI service that loads the saved model and exposes `/predict`.
- `extension/`: MV3 browser extension UI that queries the local API and displays risk.

You can tweak `train_model.py` hyperparameters to push accuracy higher on your validation splits.


### Store listing copy

- Title: URL Phishing Detector
- Short description: AI-powered phishing/malicious URL detector. Runs locally.
- Full description:
  URL Phishing Detector helps you spot risky links before you click. It analyzes the active tab’s URL locally using a trained model and shows a clear risk indicator. Nothing leaves your machine.

  Highlights:
  - One-click scan from the toolbar
  - Local inference; no data sent to servers
  - Fast, lightweight checks on URL structure
  - Clear “Likely safe”/“High risk” guidance with probability

  Requirements:
  - Run the local API at http://localhost:8000 while using the extension.

  Support: Open an issue in this repository.


>>>>>>> 1d6ce02 (changed name)
