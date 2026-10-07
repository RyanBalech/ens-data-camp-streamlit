# Allocation Lab

A containerized Streamlit workspace for exploring QRT allocation histories and inspecting held-out ML predictions. Individual application adaptation by **Ryan Balech**, building on the ENS Data Camp team project.

The app joins feature and target files by validated row identifiers, explores 20-day return and signed-volume signals, and serves an offline CatBoost/logistic-regression evaluation. React/Framer Motion, Altair and native Streamlit controls provide responsive charts, fullscreen views and PNG/JSON/CSV exports.

## Run with Docker

```bash
git clone https://github.com/RyanBalech/ens-data-camp-streamlit.git
cd ens-data-camp-streamlit
docker compose up --build
```

Open **http://localhost:8501**. Stop with `docker compose down`. Repository access is required while the source remains private.

The default demo contains **360 deterministic synthetic observations** and needs no download. Upload matching challenge training CSVs to explore the original **527,073 observations**. Data are processed on the app server; original training files are excluded from the image and repository.

The image uses a digest-pinned Python base, locked dependencies, a non-root runtime and an HTTP health check. The compiled frontend is bundled locally; running the app requires neither Node nor a GPU.

## ML evaluation

Model Lab displays a separate offline experiment on **60,000 real observations** with **three disjoint date-grouped folds** and train-fold preprocessing.

| Model | Held-out accuracy |
| --- | ---: |
| CatBoost | 51.45% |
| Logistic regression | 51.12% |
| Training-fold majority | 50.79% |

The app supports threshold selection, confusion matrices and model-derived feature importance without retraining during page interactions. Anonymized date identifiers permit grouped validation but do not establish chronological performance or trading profitability. [Evaluation artifacts and reproduction](results/README.md) include input hashes, settings and per-fold results.

## Development and validation

```bash
python -m pip install -r requirements.txt
python -m pytest --cov=hec --cov-report=term-missing --cov-fail-under=95
python -m streamlit run app.py
```

GitHub CI runs unit/app tests, checks the frontend build and builds the Docker image, then verifies its health endpoint and browser interactions. The existing GitLab configuration is retained for the original course environment.

Browser checks cover chart rendering, fullscreen/resizing, exports, responsive widths and threshold endpoints:

```bash
python -m pip install -r requirements-browser.txt
python -m playwright install chromium
python scripts/check_browser.py
```

See the [setup and data-contract guide](docs/reproduction.md) for full uploads, browser options and frontend development.

## Implementation

- `hec/tools/`: import contracts, deterministic demo generation, row-local features and threshold metrics.
- `ui/`, `assets/`, `frontend/`: chart controls, research views and bundled motion header.
- `scripts/evaluate.py`, `results/evaluation.json`: offline experiment and aggregate evidence.
- `tests/`, `.github/workflows/`, `Dockerfile`: automated validation and packaging.

Original research team: Omar Karim, Ryan Balech, Hitaishi Dhoowooah, Gabriel Dreik and Korouhanba Khuman Laikhuram. The historical notebook is retained as a reference; the new app evaluation is reported separately. [Course requirement mapping](ASSESSMENT.md).
