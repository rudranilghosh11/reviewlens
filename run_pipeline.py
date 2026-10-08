"""CLI: python run_pipeline.py [path.csv]  -> writes outputs/ (issues.csv, aspect_summary.csv, brief.md)"""
import sys
from src.pipeline import run_all, find_issues, emerging, aspect_summary
from src.brief import make_brief

path = sys.argv[1] if len(sys.argv) > 1 else "data/reviews.csv"
reviews, a = run_all(path)
issues, alerts = find_issues(a, reviews), emerging(a)
issues.drop(columns=["quotes"]).to_csv("outputs/issues.csv", index=False)
aspect_summary(a).to_csv("outputs/aspect_summary.csv")
open("outputs/brief.md", "w").write(make_brief("All brands", reviews, a, issues, alerts))
print(open("outputs/brief.md").read())
