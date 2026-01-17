## URL Phishing Detector

AI-powered phishing / malicious URL classifier backed by a high-accuracy XGBoost model, exposed via a FastAPI backend and a premium-style browser extension UI.

### 1. Environment setup

- **Create a virtualenv (recommended)**:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- **Install dependencies**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Train the model

The dataset `web-page-phishing.csv` is already in the project root. To train and persist the model:

```bash
python train_model.py
```

This will:

- Train an **XGBoost** classifier on the numeric URL-structure features.
- Print a validation **classification report** and **ROC-AUC**.
- Save the model bundle to `model/phishing_model.joblib`.

### 3. Run the API server

Start the FastAPI app (after training the model at least once):

```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Test it quickly:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

You should see JSON with `is_phishing` and `probability_phishing`.

### 4. Load the browser extension

1. Open Chrome / Edge / any Chromium-based browser.
2. Go to `chrome://extensions`.
3. Enable **Developer mode** (top-right).
4. Click **Load unpacked** and select the `extension` folder inside this project.

The extension:

- Reads the **current tab URL**.
- Sends it to your local API at `http://localhost:8000/predict`.
- Renders the result in an **Apple-like, minimal glassmorphism UI** with risk meter and messaging.

### 5. How the model works

- `url_features.py` defines a **feature extractor** that matches the dataset columns:
  - URL length, counts of `.`, `-`, `_`, `/`, `?`, `=`, `@`, `&`, `!`, space, `~`, `,`, `+`, `*`, `#`, `$`, `%`, and a heuristic **redirection** count.
- `train_model.py`:
  - Loads `web-page-phishing.csv`.
  - Trains a **scaled numeric pipeline + XGBoost** classifier.
  - Saves the trained pipeline and feature metadata.
- `api.py`:
  - Loads the saved pipeline.
  - On `/predict`, extracts URL features server-side and returns a **probability of phishing**.

You can tweak `train_model.py` hyperparameters to push accuracy even higher if you benchmark on your own validation splits.
