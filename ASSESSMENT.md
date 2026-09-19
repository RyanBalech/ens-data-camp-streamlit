# Assignment evidence

This maps the supplied assignment brief to reviewable repository evidence. It is not an instructor approval or grade prediction.

| Requirement | Evidence |
| --- | --- |
| Prior or personal data science project | ENS Data Camp / QRT research, preserved in `ensdata_original.ipynb`; original collaborators credited in the README and app. |
| Individual Streamlit adaptation | `app.py`, `ui/` and `hec/tools/`; Ryan Balech's adaptation and original team work are distinguished. |
| Containerized application | Root `Dockerfile`, health endpoint, pinned Python base, and build/run instructions in `README.md`. |
| Documentation in a Git project | README covers setup, inputs, features, research limitations, tests and submission; `results/README.md` covers offline evaluation. |
| Tests on importing and filtering | `tests/test_data_utils.py` covers ID-based joins, label creation, duplicates, missing/invalid data, mismatched IDs, filters, empty results and preservation of source data. |
| Associated CI process | `.gitlab-ci.yml` runs pytest with a 95% utility coverage gate and JUnit/Cobertura reports, browser checks, and a reproducible frontend build check. |
| Reproducibility | Complete runtime and model dependency locks, a pinned container base, fixed seeds, input hashes, and executable evaluation code. |
| Repository link for submission | `https://gitlab.code.hfactory.io/ryan.balech/ens-data-camp-streamlit` |
| Optional public image | DockerHub publication is optional in the supplied brief. Reviewers can build the image from the repository. |

## Reviewer access and data

The repository is private. Confirm that the assessor can open and clone it before submission; this audit cannot identify the assessor's account or confirm their access.

The app runs immediately with 360 explicitly synthetic observations and committed aggregate evidence from a separate real-data experiment. Reproducing that experiment requires the original challenge training files, which are excluded from Git. Data-access instructions and the exact reproduction command are in the README and results README. If confidentiality prevents the release required by the course, follow the brief's instruction to contact the teaching team via Slack.

## Verify the current version

Build the image and run `docker run --rm ens-data-camp python -m pytest --cov=hec --cov-report=term-missing`. Inspect the pipeline for the latest commit in GitLab; a previous successful pipeline does not certify later edits. Browser tests additionally verify visible chart marks, figure expansion, downloads, threshold changes and responsive layout. Original-data uploads are checked locally because the private files are not available to CI.
