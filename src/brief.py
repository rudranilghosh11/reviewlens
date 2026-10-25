"""Auto-generated one-page PM brief (markdown)."""
import pandas as pd

def make_brief(brand, reviews, a, issues, alerts):
    base = reviews[~reviews.flagged]
    lines = [f"# ReviewLens brief: {brand}",
             f"*{len(base):,} usable reviews, {base.date.min():%d %b %Y} to {base.date.max():%d %b %Y}. "
             f"Average rating {base.rating.mean():.2f}. {int(reviews.flagged.sum())} reviews excluded as duplicate/spam-like.*", ""]
    if len(alerts):
        lines.append("## Emerging issues (act first)")
        lines += [f"- **{r.brand} / {r.aspect}**: {r.recent} negative mentions in 14 days vs ~{r.expected} expected ({r.spike}x)"
                  for r in alerts.itertuples()]
        lines.append("")
    lines.append("## Top 5 things to fix")
    for i, r in enumerate(issues.head(5).itertuples(), 1):
        arrow = "rising" if r.trend > 0.15 else "falling" if r.trend < -0.15 else "stable"
        lines += [f"{i}. **{r.issue}** ({r.aspect}, priority {r.priority}/100, {arrow})",
                  f"   - Affects {r.pct_reviews}% of reviews; owner: {r.owner}",
                  f"   - Evidence: \"{r.quotes[0]}\"" + (f"; \"{r.quotes[1]}\"" if len(r.quotes) > 1 else ""),
                  f"   - Suggested action: {r.action}"]
    return "\n".join(lines)
