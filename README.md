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
4. Explore **Overview**, **Historical signals**, **Data explorer** and **Research & methods**.

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

**The application is exploratory.** It displays observed outcomes and does not train the original model or generate forecasts. A 50.7% positive-return share is a class balance statistic, not prediction accuracy. Basis points make small returns legible: 1 bp = 0.0001 in decimal return units.

The notebook uses stratified random cross-validation. The original report describes both grouped and stratified validation, so its validation descriptions are inconsistent. This app does not assert that those scores have been reproduced. Random splits can share anonymized dates; a future modeling extension should use date-grouped validation and learn preprocessing only from training folds. Cohort plots are descriptive, not a trading backtest.

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

GitLab CI uses the same pinned Python base and locked dependencies. It compiles the app, tests import/filter edge cases and Streamlit execution, and publishes JUnit and coverage reports. The utility coverage gate is 95%. UI smoke tests also change filters and exercise the upload waiting state, catching errors that a health endpoint cannot detect.

## Project map

- `app.py`: Streamlit workspace and aggregated charts.
- `assets/style.css`, `.streamlit/config.toml`: visual system and server settings.
- `hec/tools/data_utils.py`: validated import and filtering.
- `tests/`: data contracts, filtering and Streamlit execution tests.
- `sample_data/`: six-row synthetic demonstration pair.
- `ensdata_original.ipynb`: historical project reference; has original local paths and GPU assumptions, and is not required to run the app.
- `Dockerfile`, `requirements.lock`, `.gitlab-ci.yml`: reproducible packaging and automated verification.

## Submission

Submit this repository URL. DockerHub is optional. Ensure the assessor can access this private repository; a localhost URL is only usable on the machine running the container.

The assignment asks for a prior/personal data science project adapted to Streamlit, containerized, documented, with data import/filter tests and CI. This repository maps those requirements to the files above. It makes no claim of instructor approval or reproduced CatBoost performance.
