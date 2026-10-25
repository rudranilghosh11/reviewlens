"""Evaluation: per-aspect precision/recall/F1 + Cohen's kappa between raters.
Usage:
  python -m src.evaluate --make-template 250        # sample reviews for the team to hand-label
  python -m src.evaluate --gold data/labels_gold_synthetic.csv
  python -m src.evaluate --gold rater1.csv --rater2 rater2.csv   # inter-annotator agreement
Label values per aspect: pos / neg / none."""
import argparse, pandas as pd
from sklearn.metrics import classification_report, cohen_kappa_score, f1_score
from .pipeline import run_all
from .config import ASPECT_RE

def predict_labels(reviews, a):
    rows = []
    g = a.groupby("review_id")
    for rid in reviews.review_id:
        lab = {x: "none" for x in ASPECT_RE}
        if rid in g.groups:
            for asp, s in g.get_group(rid).groupby("aspect").sentiment:
                lab[asp] = "neg" if (s == "neg").any() else "pos" if (s == "pos").any() else "none"
        rows.append(dict(review_id=rid, **lab))
    return pd.DataFrame(rows)

def evaluate(gold_path, data="data/reviews.csv", out="outputs/eval_report.md"):
    reviews, a = run_all(data)
    gold = pd.read_csv(gold_path)
    pred = predict_labels(reviews, a).set_index("review_id").loc[gold.review_id]
    gold = gold.set_index("review_id")
    lines = ["# Evaluation report", f"Gold file: `{gold_path}` ({len(gold)} reviews)", "",
                  "| Aspect | Precision (neg) | Recall (neg) | F1 (neg) | Macro-F1 (pos/neg/none) |", "|---|---|---|---|---|"]
    f1s = []
    for asp in [x for x in ASPECT_RE if x in gold.columns]:  # only topics present in the gold file
        y, p = gold[asp], pred[asp]
        rep = classification_report(y, p, labels=["neg"], output_dict=True, zero_division=0)["neg"]
        mf = f1_score(y, p, average="macro", zero_division=0); f1s.append(mf)
        lines.append(f"| {asp} | {rep['precision']:.2f} | {rep['recall']:.2f} | {rep['f1-score']:.2f} | {mf:.2f} |")
    lines += ["", f"**Mean macro-F1 across aspects: {sum(f1s)/len(f1s):.2f}**"]
    open(out, "w").write("\n".join(lines)); print("\n".join(lines))

def kappa(f1, f2):
    a, b = pd.read_csv(f1).set_index("review_id"), pd.read_csv(f2).set_index("review_id")
    common = a.index.intersection(b.index)
    for asp in [x for x in ASPECT_RE if x in a.columns and x in b.columns]:
        print(f"{asp:13s} kappa = {cohen_kappa_score(a.loc[common, asp], b.loc[common, asp]):.2f}")

def make_template(n, data="data/reviews.csv"):
    r = pd.read_csv(data).sample(n, random_state=7)[["review_id", "review_text"]]
    for asp in ASPECT_RE: r[asp] = ""
    r.to_csv("data/label_template.csv", index=False); print(f"Wrote data/label_template.csv ({n} rows)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold"); ap.add_argument("--rater2"); ap.add_argument("--make-template", type=int)
    x = ap.parse_args()
    if x.make_template: make_template(x.make_template)
    elif x.gold and x.rater2: kappa(x.gold, x.rater2)
    elif x.gold: evaluate(x.gold)
    else: ap.print_help()
