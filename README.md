# MailGuard AI — Spam Detection & Email Security Analytics

MailGuard AI is an end-to-end NLP security project that combines classical machine learning, a local REST API, persistent analytics, an interactive security dashboard, and a Manifest V3 Chrome Extension.

## Highlights

- TF-IDF based NLP preprocessing
- Comparison of Naive Bayes, Logistic Regression, Linear SVM and Random Forest
- Accuracy, precision, recall, F1 and ROC-AUC evaluation
- Confusion-matrix artifact and model comparison CSV
- Confidence-aware predictions
- Measurable text signals such as URLs, urgency terms, currency indicators and capitalization
- Flask REST API
- SQLite prediction history
- Deterministic seeded demo activity
- Interactive analytics dashboard with charts
- Prediction history and dataset insights
- Manifest V3 Chrome Extension
- Extension popup, content script, background service worker and options page
- Local-first architecture with no external AI API required
- Pytest API smoke tests

## Architecture

```text
Chrome Extension / Dashboard
          |
          v
      Flask REST API
          |
     Service Layer
      /        \
 Prediction   Analytics
 Service       Service
      \        /
       SQLite + ML Artifacts
              |
       TF-IDF + Classifier
```

## Existing model evaluation

The repository retains the original held-out evaluation artifacts in `models/metadata.json` and `models/model_comparison.csv`. The dashboard reads those files rather than inventing performance values.

Current selected-model artifact: Random Forest.

## Project structure

```text
backend/
  api/routes.py
  services/prediction_service.py
  services/database.py
  services/analytics_service.py

dashboard/
  templates/dashboard.html
  static/css/dashboard.css
  static/js/dashboard.js

extension/
  manifest.json
  popup/
  content/
  background/
  options/
  assets/

ml artifacts/
  models/
  data/
  assets/

tests/
scripts/
```

## Run locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python run.py
```

Open `http://127.0.0.1:5000`.

The first application start automatically initializes SQLite and seeds deterministic demo activity. Demo records are marked separately from model evaluation metrics.

To seed manually:

```bash
python scripts/seed_demo_data.py
```

## API

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | Backend/model health |
| `GET /api/model` | Selected model and metadata |
| `GET /api/metrics` | Model comparison |
| `GET /api/analytics` | Activity analytics |
| `GET /api/dataset` | Dataset statistics |
| `GET /api/history` | Recent predictions |
| `POST /api/predict` | Analyze a message |
| `DELETE /api/history/demo` | Clear seeded demo activity |

Example:

```json
POST /api/predict
{
  "message": "URGENT! Claim your free reward now at http://example.invalid"
}
```

## Chrome Extension

1. Start the Flask application.
2. Open Chrome → `chrome://extensions`.
3. Enable **Developer mode**.
4. Select **Load unpacked**.
5. Choose the repository's `extension/` directory.
6. Pin MailGuard AI.
7. Open a page containing email/message text and use **Analyze Current Page**.

The extension defaults to `http://127.0.0.1:5000`. This can be changed from its Settings page.

The extension is intentionally designed for local/development use and is not packaged as a Chrome Web Store deployment.

## Dashboard sections

- **Overview:** KPIs, detection activity, class distribution and model metrics
- **Detector:** interactive message classification and signal inspection
- **Analytics:** risk and confidence distributions
- **Model Performance:** model comparison and configuration
- **Prediction History:** persistent prediction records with demo-data controls
- **Dataset Insights:** dataset composition and descriptive statistics
- **System:** runtime, architecture and privacy information

## Testing

Run:

```bash
pytest -q
```

## Notes

The dashboard distinguishes seeded activity from held-out ML evaluation. Confidence is derived from the classifier output; the displayed signals are supplementary text indicators and are not claimed to be causal explanations of the model.
