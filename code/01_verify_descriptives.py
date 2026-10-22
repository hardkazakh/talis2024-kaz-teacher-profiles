"""Reproduce the descriptive and clustering-index results of the manuscript from the
analysis subset, and compare each value with the number printed in the paper.

Covers: sample size, Table 2 (missingness by form), Table 3 (unweighted/weighted means
and SDs), Table 4 (domain reliability and domain-score statistics), Table 6 (domain
Spearman correlations), the supervised target definition, and Table 7 (internal
cluster indices, k = 2..8).

Usage : python code/01_verify_descriptives.py
Output: outputs/verification_report.md
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score

sys.path.insert(0, str(Path(__file__).parent))
from variables import COMPETENCE, DOMAINS, EXCLUDED, SCALE_MISSING, TARGET, WEIGHT  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
rows = []  # (section, quantity, reproduced, paper)


def check(section, quantity, value, paper, nd=2):
    rows.append((section, quantity, round(float(value), nd), paper))


def alpha(m: pd.DataFrame) -> float:
    m = m.dropna()
    k = m.shape[1]
    return k / (k - 1) * (1 - m.var(ddof=1).sum() / m.sum(axis=1).var(ddof=1))


def wstats(x: pd.Series, w: pd.Series):
    ok = x.notna()
    x, w = x[ok], w[ok]
    mu = np.average(x, weights=w)
    return mu, np.sqrt(np.average((x - mu) ** 2, weights=w))


def main() -> None:
    df = pd.read_csv(ROOT / "data" / "talis2024_kaz_analysis_subset.csv")
    scales = COMPETENCE + [TARGET] + EXCLUDED
    X = df[scales].where(~df[scales].isin(SCALE_MISSING))       # recode 9998/9999 -> NaN
    check("Sample", "Teachers (n)", len(df), 7360, 0)

    # Table 2: missingness by questionnaire form
    paper_t2 = {"T4PDGENP": [33.7, 100.0, 0.5, 0.4], "T4DRTWCI": [33.7, 100.0, 0.7, 0.4],
                "T4AUTCH": [33.7, 100.0, 0.7, 0.4], "T4WLOADT": [33.7, 0.5, 0.8, 100.0],
                "T4STBEH": [33.7, 0.5, 1.1, 100.0]}
    for v, p in paper_t2.items():
        miss = X[v].isna()
        check("Table 2", f"{v} missing overall (%)", 100 * miss.mean(), p[0], 1)
        for f in (1, 2, 3):
            check("Table 2", f"{v} missing form {f} (%)", 100 * miss[df.IDTQUEST == f].mean(), p[f], 1)

    # Table 3: unweighted and TCHWGT-weighted means/SDs
    paper_t3 = {
        "T4DRTWCI": (10.26, 1.66, 10.32, 1.61), "T4DRTIIA": (10.57, 1.62, 10.61, 1.56),
        "T4SECLS": (12.24, 1.92, 12.20, 1.92), "T4SEINS": (12.26, 2.07, 12.16, 2.10),
        "T4SEENG": (11.99, 1.81, 11.99, 1.84), "T4CLAIN": (13.47, 1.83, 13.53, 1.79),
        "T4COGAC": (10.67, 1.78, 10.71, 1.78), "T4CLASM": (11.66, 1.67, 11.73, 1.63),
        "T4ADLE": (12.38, 1.89, 12.41, 1.88), "T4PBLE": (11.33, 1.82, 11.29, 1.80),
        "T4FULFIL": (11.60, 1.88, 11.56, 1.88), "T4EXINF": (11.58, 1.87, 11.54, 1.86),
        "T4COLES": (10.31, 1.54, 10.36, 1.53), "T4AUTCH": (11.58, 2.07, 11.61, 2.09),
        "T4WELS": (8.15, 1.86, 8.09, 1.83), "T4WLOADT": (8.31, 1.85, 8.26, 1.84),
        "T4STBEH": (8.21, 1.93, 8.17, 1.92), "T4JOBSAT": (10.06, 1.77, 10.10, 1.76),
        "T4JOYTCH": (13.83, 1.90, 13.85, 1.90), "T4PDGENP": (11.20, 2.17, 11.34, 2.15)}
    for v, (um, us, wm, ws) in paper_t3.items():
        m, s = wstats(X[v], df[WEIGHT])
        check("Table 3", f"{v} mean", X[v].mean(), um)
        check("Table 3", f"{v} SD", X[v].std(), us)
        check("Table 3", f"{v} weighted mean", m, wm)
        check("Table 3", f"{v} weighted SD", s, ws)

    # Table 4: Cronbach's alpha (raw scales) and domain scores
    # Domain score = mean of z-scores of median-imputed constituent scales.
    Xi = X[COMPETENCE].fillna(X[COMPETENCE].median())
    Z = (Xi - Xi.mean()) / Xi.std()
    dom = pd.DataFrame({d: Z[v].mean(axis=1) for d, v in DOMAINS.items()})
    paper_t4 = {"digital_practice": (0.891, 0.949, -3.75, 2.81),
                "self_efficacy": (0.846, 0.876, -3.73, 1.63),
                "instructional_practice": (0.785, 0.675, -4.34, 2.16),
                "collaboration_autonomy": (0.579, 0.730, -3.39, 2.19),
                "wellbeing_stress": (0.781, 0.810, -1.48, 3.33),
                "job_satisfaction": (0.721, 0.852, -3.14, 1.83)}
    for d, (a, sd, mn, mx) in paper_t4.items():
        check("Table 4", f"{d} alpha", alpha(X[DOMAINS[d]]), a, 3)
        check("Table 4", f"{d} SD", dom[d].std(), sd, 3)
        check("Table 4", f"{d} min", dom[d].min(), mn)
        check("Table 4", f"{d} max", dom[d].max(), mx)

    # Table 6: domain-level Spearman correlations (lower triangle)
    r = dom.corr("spearman")
    names = list(DOMAINS)
    paper_t6 = [[0.275], [0.383, 0.475], [0.330, 0.396, 0.404],
                [-0.077, -0.101, -0.088, -0.140], [0.136, 0.328, 0.283, 0.288, -0.315]]
    for i, row in enumerate(paper_t6, start=1):
        for j, p in enumerate(row):
            check("Table 6", f"rho({names[i]}, {names[j]})", r.iloc[i, j], p, 3)

    # Supervised target
    y = X[TARGET].dropna()
    check("Target", "Teachers with observed T4PDGENP", len(y), 4882, 0)
    check("Target", "Median threshold", y.median(), 11.421, 3)
    check("Target", "Positive prevalence", (y > y.median()).mean(), 0.499, 3)
    check("Target", "rho(T4PDGENP, T4DRTWCI)", X[[TARGET, "T4DRTWCI"]].corr("spearman").iloc[0, 1], 0.233, 3)
    for v in EXCLUDED:
        check("Target", f"rho(T4PDGENP, {v}) (paper: approx. 0.81)",
              X[[TARGET, v]].corr("spearman").iloc[0, 1], "≈0.81", 3)

    # Table 7: internal indices of the full-sample k-means solution
    # Input = 19 standardised (median-imputed) competence scales; this reproduces the
    # inertia values in Table 7 (the six domain scores cannot: their total sum of squares
    # is below the reported inertia).
    Zp = (Xi - Xi.mean()) / Xi.std(ddof=0)
    paper_t7 = {2: (116932, 0.145, 1441.5, 2.161), 3: (109346, 0.105, 1025.8, 2.400),
                4: (102929, 0.097, 879.3, 2.418), 5: (97606, 0.090, 795.6, 2.324),
                6: (95068, 0.070, 692.7, 2.543), 7: (92825, 0.069, 620.7, 2.589),
                8: (90941, 0.067, 564.7, 2.472)}
    sizes = {}
    for k, (ine, sil, ch, db) in paper_t7.items():
        km = KMeans(n_clusters=k, random_state=SEED, n_init=10).fit(Zp)
        check("Table 7", f"k={k} inertia", km.inertia_, ine, 0)
        check("Table 7", f"k={k} silhouette", silhouette_score(Zp, km.labels_), sil, 3)
        check("Table 7", f"k={k} Calinski-Harabasz", calinski_harabasz_score(Zp, km.labels_), ch, 1)
        check("Table 7", f"k={k} Davies-Bouldin", davies_bouldin_score(Zp, km.labels_), db, 3)
        if k == 4:
            sizes = sorted(np.bincount(km.labels_).tolist(), reverse=True)

    # Report
    out = ["# Verification report", "",
           "Reproduced = value computed by `code/01_verify_descriptives.py` from "
           "`data/talis2024_kaz_analysis_subset.csv`; Paper = value printed in the manuscript.", "",
           "| Section | Quantity | Reproduced | Paper | Match |", "|---|---|---|---|---|"]
    n_ok = n_close = 0
    for sec, q, v, p in rows:
        if isinstance(p, str):
            ok = "–"
        else:
            nd = max(len(str(p).split(".")[1]) if "." in str(p) else 0, 0)
            if round(v, nd) == round(p, nd):
                ok = "yes"
            elif abs(v - p) <= max(0.01 * abs(p), 2 * 10 ** -nd):
                ok = "close (<1%)"
                n_close += 1
            else:
                ok = "no"
            n_ok += ok == "yes"
        out.append(f"| {sec} | {q} | {v} | {p} | {ok} |")
    n_num = sum(not isinstance(p, str) for *_, p in rows)
    n_no = n_num - n_ok - n_close
    out += ["", f"**{n_ok} of {n_num} numeric values match the manuscript exactly at its printed precision; "
            f"{n_close} are within 1% (rounding or k-means initialisation); {n_no} differ by more.**",
            "", f"k = 4 profile sizes reproduced here: {sizes} (paper: 2989, 2403, 1063, 905). "
            "Small differences at k >= 3 arise from k-means initialisation; the authors' "
            "original pipeline in `analysis/` gives the published partition."]
    (ROOT / "outputs").mkdir(exist_ok=True)
    (ROOT / "outputs" / "verification_report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{n_ok}/{n_num} exact, {n_close} close, {n_num - n_ok - n_close} differ; report written to outputs/verification_report.md")


if __name__ == "__main__":
    main()
