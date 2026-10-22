# Minimal dataset and code: Person-Centred Modelling of Teacher Professional Competence with Explainable Machine Learning

This repository holds the minimal dataset, metadata and code supporting the article:

> Baizhanov, N.; Sharimbayev, B.; Shinetova, L.; Khamitova, K.; Kazin, A.; Akhmetov, A. Person-Centred Modelling of Teacher Professional Competence with Explainable Machine Learning. *Mathematics* (submitted, 2026).

The study analyses the OECD Teaching and Learning International Survey (TALIS) 2024 ISCED level 2 teacher public-use file for Kazakhstan (7,360 teachers). It applies three methods:

- k-means profiling of 19 competence scales;
- prediction of elevated general-pedagogy professional-development (PD) need with five model families;
- SHAP explanation of the fitted models.

## Contents

```
data/
  talis2024_kaz_analysis_subset.csv   primary data: 7,360 teachers x 34 variables (original OECD codes)
  codebook.csv                        variable definitions, roles, valid values, missing codes, counts
code/
  variables.py                        variable lists and missing-value codes used by all scripts
  00_extract_subset.py                rebuilds the subset from the OECD file (btgintt4.csv)
  01_verify_descriptives.py           reproduces Tables 2, 3, 4, 6, 7 and the target definition
analysis/                             authors' original modelling pipeline (Tables 5, 8-11, Figures 1-8)
outputs/
  verification_report.md              reproduced values vs. values printed in the paper
requirements.txt                      Python package versions
DATA_LICENSE.md                       OECD terms of use for the data
LICENSE                               MIT licence for the code
CITATION.cff                          how to cite this repository
```

## Data

**Source.** OECD (2025), *TALIS 2024 Database*, public-use teacher file `btgintt4.csv`, available at <https://www.oecd.org/en/data/datasets/talis-2024-database.html>. The rows are filtered to `CNTRY == "KAZ"`. File version 3.2, IEA release date 2025-11-05, as recorded in the `VERSION` and `IEADATE` fields of the original file.

**What the subset contains.** It holds all variables used in the study:

- 5 identifier and design variables;
- 19 competence scales in six domains;
- the PD-need target `T4PDGENP` and the two excluded sibling scales;
- 6 teacher-background variables;
- the final teacher weight `TCHWGT`.

Values are exactly as distributed by the OECD; nothing is recoded in the file. Full definitions are in `data/codebook.csv`. Item wording and category labels are documented in the OECD TALIS 2024 technical documentation and codebook.

**Scale scores.** These are OECD-constructed item-response-theory scores on a common metric, so they are comparable in units but not centred at zero.

**Missing-value codes.** The code meanings were checked against the questionnaire form `IDTQUEST` in this extract:

| Variable type | Not administered (rotated form) | Omitted / invalid |
|---|---|---|
| Scale scores (`T4…` scales) | 9998 | 9999 |
| One-digit categorical | 8 | 9 |
| `T4TYQUAL` (two-digit categorical) | 98 | 99 |

TALIS uses three rotated questionnaire forms:

- **Form 1:** digital practice, five instructional-practice scales, autonomy, the PD-need scales and class size were not administered.
- **Form 3:** workload stress, behaviour stress, joy of teaching, education level and qualification route were not administered.

This structure produces the ≈33.7% missingness discussed in Section 3.3 of the paper. Codes 9998/8/98 are therefore missing by design and must not be imputed as ordinary non-response without care.

**Replicate weights.** The 100 replicate weights (`TRWGT1`–`TRWGT100`) were not used in the study and are not included. They are available in the OECD file.

**Privacy.** The data come from the OECD's anonymised public-use file. It contains no names or direct identifiers, and `IDSCHOOL`/`IDTEACH` are anonymised OECD codes. No new data were collected.

## Reproducing the results

Requirements: Python 3.10 or later and the packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt
python code/01_verify_descriptives.py          # writes outputs/verification_report.md
# optional: rebuild the subset from the OECD download
python code/00_extract_subset.py path/to/btgintt4.csv
```

**Preprocessing used in the paper.**

1. Recode 9998/9999 (and 8/9, 98/99) to missing.
2. For profiling, median-impute and standardise the 19 competence scales.
3. Compute each domain score as the mean of the z-scores of its constituent scales.
4. Fit k-means on the 19 standardised scales with `random_state = 42` and k = 2–8.
5. Define the supervised target as `T4PDGENP` > 11.421 (sample median) for the 4,882 teachers with an observed value.

**Verification status.** `01_verify_descriptives.py` reproduces 172 published numbers:

- 156 match exactly at the printed precision;
- 16 are within 1%: two differ by rounding, and the rest are k-means internal indices for k ≥ 3, which depend on initialisation;
- none differ by more than 1%.

The covered results are sample size, Table 2, Table 3, Table 4, Table 6, Table 7 and the target definition. The full comparison is in `outputs/verification_report.md`.

**Modelling results** (Tables 5 and 8–11, Figures 1–8) come from the authors' original pipeline in `analysis/`. It uses a fixed seed (42), a stratified 25% hold-out, three-fold cross-validation, and out-of-fold F1 threshold selection.

## Licences and citation

- **Code:** MIT licence (`LICENSE`).
- **Data:** OECD Terms and Conditions, which permit redistribution with attribution (`DATA_LICENSE.md`). If you reuse the data, cite the OECD as the source and keep the attribution requirement.
- **Citation:** cite the article above and this repository (`CITATION.cff`).

## Contact

Batyr Sharimbayev, SDU University, Kaskelen, Kazakhstan — batyr.sharimbayev@sdu.edu.kz
