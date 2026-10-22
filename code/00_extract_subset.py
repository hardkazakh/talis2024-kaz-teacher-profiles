"""Extract the analysis subset from the OECD TALIS 2024 ISCED 2 teacher file.

Input : the OECD public-use teacher file (btgintt4.csv, all countries) or a Kazakhstan
        extract of it. Comma- or semicolon-delimited files are both accepted.
Output: data/talis2024_kaz_analysis_subset.csv (original OECD codes retained, no recoding).

Usage : python code/00_extract_subset.py path/to/btgintt4.csv
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from variables import SUBSET  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main(src: str) -> None:
    df = pd.read_csv(src, sep=None, engine="python")      # detects ',' or ';'
    df = df[df["CNTRY"] == "KAZ"]
    missing = [v for v in SUBSET if v not in df.columns]
    if missing:
        raise SystemExit(f"Variables not found in input file: {missing}")
    out = df[SUBSET].sort_values(["IDSCHOOL", "IDTEACH"])
    dst = ROOT / "data" / "talis2024_kaz_analysis_subset.csv"
    out.to_csv(dst, index=False)
    print(f"Wrote {dst} with {out.shape[0]} rows and {out.shape[1]} columns")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
