"""Run Review Lens on the bundled normalized CSV and write a PM brief/issues CSV."""
import argparse
from pathlib import Path
import pandas as pd
from src.pipeline import run_all, aspect_summary, find_issues, emerging
from src.brief import make_brief

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/reviews.csv")
    parser.add_argument("--out", default="outputs")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    reviews, aspects = run_all(args.data)
    summary = aspect_summary(aspects) if not aspects.empty else pd.DataFrame()
    issues = find_issues(aspects, reviews)
    alerts = emerging(aspects)
    brand = str(reviews["brand"].mode().iloc[0]) if not reviews.empty else "All products"
    (out / "brief.md").write_text(make_brief(brand, reviews, aspects, issues, alerts), encoding="utf-8")
    issues.to_csv(out / "issues.csv", index=False)
    summary.to_csv(out / "aspect_summary.csv")
    alerts.to_csv(out / "emerging_alerts.csv", index=False)
    print(f"Analysed {len(reviews):,} reviews. Outputs written to {out.resolve()}.")

if __name__ == "__main__":
    main()
