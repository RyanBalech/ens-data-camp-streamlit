"""Research context with visible limitations and progressively disclosed detail."""
import streamlit as st


def research_methods():
    st.html('''<section class="methods-page" aria-labelledby="methods-title">
<header class="methods-heading"><span class="tour-kicker">RESEARCH &amp; METHODS</span>
<h2 id="methods-title">Behind the experiment.</h2>
<p>The question, the approach, and the limits of what we can conclude.</p></header>
<div class="methods-grid">
<article class="methods-panel methods-question"><span class="methods-label">THE RESEARCH QUESTION</span>
<h3>Can recent history predict the next day's direction?</h3>
<p>Each row pairs an investment allocation's trading history with its actual next-day return. The task is to predict one of two outcomes.</p>
<div class="methods-outcomes"><span><b>Positive</b>Return &gt; 0 · label 1</span><span><b>Zero or negative</b>Return ≤ 0 · label 0</span></div></article>
<article class="methods-panel"><span class="methods-label">WHAT GOES INTO A PREDICTION</span>
<div class="methods-input"><strong>20</strong><div><b>Return lags</b><span>How the allocation performed each day</span></div></div>
<div class="methods-input"><strong>20</strong><div><b>Signed-volume lags</b><span>A daily measure of trading activity</span></div></div>
<div class="methods-input"><strong>+</strong><div><b>Turnover &amp; allocation group</b><span>Liquidity and anonymized group context</span></div></div></article>
</div>
<div class="methods-flow" aria-label="Evaluation workflow"><span>Validate the data</span><i aria-hidden="true">→</i><span>Build features</span><i aria-hidden="true">→</i><span>Split by date group</span><i aria-hidden="true">→</i><span>Evaluate held-out rows</span></div>
<div class="methods-grid">
<article class="methods-panel"><span class="methods-label">EXPLORE &amp; EVALUATE</span><h3>Two ways to investigate.</h3>
<div class="methods-fact"><b>Interactive exploration</b><p>Inspect returns, compare groups and trace historical signals with demo data or your training files.</p></div>
<div class="methods-fact"><b>Fixed model evaluation</b><p>Model Lab compares CatBoost, logistic regression and a baseline on 60,000 real observations, using three disjoint date folds. Training runs offline.</p></div></article>
<article class="methods-panel"><span class="methods-label">REPRODUCIBILITY</span><h3>Built to run again.</h3>
<div class="methods-fact"><b>Packaged environment</b><p>Docker, a pinned Python image and locked dependencies keep the app environment reproducible.</p></div>
<div class="methods-fact"><b>Tested data handling</b><p>Automated import, filtering and research checks run in GitLab CI alongside browser and frontend-build checks.</p></div></article>
</div>
<aside class="methods-limits"><span class="methods-label">READ THE RESULTS WITH CONTEXT</span><h3>Evidence has boundaries.</h3>
<p>Date-grouped validation reduces same-date leakage, but anonymized dates prevent a chronological backtest. Small accuracy differences do not establish profitability or statistical significance.</p>
<p>The original notebook and report describe inconsistent validation methods. Model Lab presents a separate experiment; it does not reproduce the original reported scores.</p></aside>
<footer class="methods-credits"><div><span class="methods-label">INDIVIDUAL APP ADAPTATION</span><strong>Ryan Balech</strong><span>ENS Data Camp / QRT asset allocation</span></div>
<div><span class="methods-label">ORIGINAL RESEARCH TEAM</span><p>Omar Karim · Ryan Balech · Hitaishi Dhoowooah · Gabriel Dreik · Korouhanba Khuman Laikhuram</p></div></footer>
</section>''')
    with st.expander("Validation details & original research"):
        st.write("The original notebook engineers statistical, momentum and liquidity features and trains CatBoost on a GPU. Its stratified random cross-validation may place observations from the same anonymized date in both partitions. The report also describes grouped validation, so its descriptions are inconsistent.")
        st.write("The new experiment groups folds by TS and fits preprocessing on each training fold. TS values are identifiers, not calendar dates. Cohort charts describe observed outcomes; held-out model metrics are reported separately in Model Lab. Neither is a trading backtest.")
    with st.expander("Data requirements & reproducing the project"):
        st.write("Use matching X_train and y_train CSVs. X_test and submission.csv are not inputs to this labeled-data explorer. The 360-row demo is generated from a fixed seed and is explicitly synthetic. Reproducing the full analysis requires the original challenge training files.")
        st.write("The repository README explains installation, data access, tests and Docker. The results README documents the evaluation command, input hashes, fixed seed and separate model dependency lock.")
        st.code("docker build -t ens-data-camp .\ndocker run --rm -p 8501:8501 ens-data-camp\ndocker run --rm ens-data-camp python -m pytest --cov=hec", language="bash")
        st.link_button("Open the repository & setup guide", "https://gitlab.code.hfactory.io/ryan.balech/ens-data-camp-streamlit")
