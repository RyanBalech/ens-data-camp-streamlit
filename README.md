# ENS Data Camp Return Explorer

This project turns the ENS Data Camp financial classification work into a Streamlit app. It joins feature and target files by `ROW_ID`, derives a positive-return label, and lets users filter observations by allocation group and label.

## Run locally

Install dependencies with `pip install -r requirements.txt`, then run `streamlit run app.py`. Upload `X_train_9xQjqvZ.csv` and `y_train_Ppwhaz8.csv` in the app. The large CSV files are intentionally excluded from Git.

Run tests with `python -m pytest`.

## Run with Docker

Build with `docker build -t ens-data-camp .` and run with `docker run --rm -p 8501:8501 ens-data-camp`. Open http://localhost:8501.

The GitLab CI pipeline runs the test suite on every push.
