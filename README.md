# Allocation Lab · ENS Data Camp

An individual Streamlit adaptation by **Ryan Balech** of the ENS Data Camp / QRT asset-allocation project. Explore the relationship between historical allocation signals and the sign of observed next-day returns.

## Reviewer quick start

You need Git, Docker and access to this private HFactory repository. No Python or GPU installation is needed for Docker.

```sh
git clone https://gitlab.code.hfactory.io/ryan.balech/ens-data-camp-streamlit.git
cd ens-data-camp-streamlit
docker build -t ens-data-camp .
docker run --rm -p 8501:8501 --name allocation-lab ens-data-camp
```

Open http://localhost:8501 on the computer running Docker. If port 8501 is occupied, use `-p 8502:8501` and open http://localhost:8502. Stop with `docker stop allocation-lab`.

The **Demo dataset** opens immediately with six explicitly synthetic observations. It demonstrates the controls and charts; it is not a sample extracted from QRT data and cannot reproduce research results. No external data download is needed for the demo.

## Explore the original data

1. Select **Upload my data** in the sidebar.
2. Upload `X_train_9xQjqvZ.csv` (approximately 272 MB) and `y_train_Ppwhaz8.csv` (approximately 11 MB).
3. Select an allocation group and return direction. All metrics and charts update.
4. Explore **Overview**, **Historical signals**, **Data explorer**, **Model Lab** and **Research & methods**.
5. Change histogram bins or chart height. Scroll a chart to zoom, drag to pan and double-click to reset. Each figure has an **Expand chart** dialog and a Vega-Lite JSON export.
6. In Historical signals, inspect a specific observation's 20 return and volume lags and download its engineered features. This requires the full feature schema.
7. In Model Lab, compare held-out models, adjust the decision threshold, inspect the confusion matrix and read the model card. This fixed offline experiment is independent of sidebar dataset filters.

The original training files are obtained through the ENS Challenge Data / QRT challenge access used for the original project. They are excluded from Git and Docker; redistribution rights are not assumed. The author has these files locally. A reviewer who needs the full data must have access to the original challenge files or obtain them from the author through an allowed course channel.

The upload limit is **500 MB per file**. Files are processed on the host running the app and cached in that server's memory, not added to Git. Rebuilding/restarting the container clears its in-memory cache. On a deployed server, uploading sends the files to that server.

The supplied full training pair contains 527,073 aligned observations. Allow several seconds for the initial import and enough RAM for the CSVs, DataFrames and cache (4 GB available to Docker is a practical starting point).

### Input contract

- Features: unique, non-missing `ROW_ID`, non-missing `GROUP`; optionally `RET_1` through `RET_20`, `SIGNED_VOLUME_1` through `SIGNED_VOLUME_20`, `TS`, `ALLOCATION`, `MEDIAN_DAILY_TURNOVER`.
- Targets: unique, non-missing `ROW_ID` and finite numeric `target`.
- Both files must contain exactly the same identifier set. Rows are aligned by ID, never by file order.
- Empty files, duplicate IDs, invalid targets and mismatched IDs are rejected with a clear message.
- Label 1 means `target > 0`; label 0 includes zero and negative returns.
- Missing historical features are preserved and shown in the quality table. Lag means exclude missing values.
- `TS` is an anonymized identifier, not a real calendar date.
- `X_test` and `submission.csv` are not inputs: this explorer requires known targets.

## Research scope and attribution

The original project investigates whether 20-day return and signed-volume histories, turnover and allocation group can predict next-day return direction. The supplied `ensdata_original.ipynb` engineers momentum, volatility, liquidity and group-relative features before fitting GPU CatBoost.

Original research collaborators: Omar Karim, Ryan Balech, Hitaishi Dhoowooah, Gabriel Dreik and Korouhanba Khuman Laikhuram. This application's interface, import/filter pipeline, tests and packaging form Ryan's individual adaptation.

**The application combines exploration and verified offline evaluation.** It does not train models during page interactions. Model Lab displays a new CPU CatBoost and logistic-regression experiment with 60,000 real observations and three date-grouped folds. It includes held-out threshold metrics and model-derived feature importance. A 50.7% positive-return share in the dataset overview is still a class balance statistic, not prediction accuracy. Basis points make small returns legible: 1 bp = 0.0001 in decimal return units.

The notebook uses stratified random cross-validation. The original report describes both grouped and stratified validation, so its validation descriptions are inconsistent. The new experiment uses date-grouped validation and train-fold preprocessing; its results are explicitly separate from the report. Cohort plots are descriptive, not a trading backtest. See [evaluation evidence and reproduction commands](results/README.md).

## Local Python setup and tests

Python **3.10** is the supported reproducibility environment. The Docker base is pinned by digest and the complete resolved dependency set is in `requirements.lock`.

```sh
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux instead: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest --cov=hec --cov-report=term-missing
python -m streamlit run app.py
```

Run the exact packaged tests without installing Python locally:

```sh
docker run --rm ens-data-camp python -m pytest --cov=hec --cov-report=term-missing
```

For browser-level checks against a running container, install `requirements-browser.txt`,
run `python -m playwright install chromium`, then run
`python scripts/check_browser.py`. On Windows with Edge installed, use
`python scripts/check_browser.py --channel msedge`. Add
`--data-dir "/absolute/path/to/ENS Data Camp"` to also verify the original
527,073-row upload and observation explorer. The script exercises explicit chart
expansion, native fullscreen, resizing, zoom/pan/reset, PNG/JSON/CSV exports,
threshold endpoints and responsive widths, saving evidence under ignored `artifacts/e2e/`.

GitLab's unit-test job uses the same pinned Python base and locked dependencies as Docker. It compiles the app, tests import/filter and research calculations, checks evaluation-artifact consistency and Streamlit execution, and publishes JUnit and coverage reports. The utility coverage gate is 95%. A separate Playwright browser job verifies figure controls, downloads and Model Lab interactions using the bundled demo and real aggregate evaluation evidence; the full private training files are only exercised locally. A third job checks the reproducibility of the Framer Motion frontend build.

## Project map

### Motion frontend

The research header is a React component animated with Framer Motion, embedded through Streamlit's custom-component API. It uses a stable key so filter reruns do not replay the entrance animation. Native Streamlit cards and tabs use complementary CSS transitions. Both honor the operating system's reduced-motion preference.

The compiled JavaScript and third-party license notices are committed under `assets/motion/` and served locally. Docker reviewers do not need Node or a CDN connection. To edit the animation, use Node 24.19.0, run `npm ci --ignore-scripts` and `npm run build` from `frontend/`, then commit the source, lockfile and built assets together. GitLab CI rebuilds and checks the committed bundle for reproducibility.

- `app.py`: Streamlit workspace and aggregated charts.
- `assets/style.css`, `.streamlit/config.toml`: visual system and server settings.
- `hec/tools/data_utils.py`: validated import and filtering.
- `tests/`: data contracts, filtering and Streamlit execution tests.
- `hec/tools/research.py`: tested row-local feature engineering and threshold metrics.
- `ui/`: chart expansion/export and research pages.
- `scripts/evaluate.py`, `requirements-model.lock`: separately reproducible offline CPU experiment.
- `results/evaluation.json`: verified aggregate validation evidence and input hashes.
- `sample_data/`: six-row synthetic demonstration pair.
- `ensdata_original.ipynb`: historical project reference; has original local paths and GPU assumptions, and is not required to run the app.
- `Dockerfile`, `requirements.lock`, `.gitlab-ci.yml`: reproducible packaging and automated verification.

## Submission

Submit this repository URL. DockerHub is optional. Ensure the assessor can access this private repository; a localhost URL is only usable on the machine running the container.

The assignment asks for a prior/personal data science project adapted to Streamlit, containerized, documented, with data import/filter tests and CI. This repository maps those requirements to the files above. It makes no claim of instructor approval or reproduced CatBoost performance.
