# ReviewLens: Customer Voice Insights for Brands

Turns thousands of product reviews into a **prioritised, evidence-backed "fix first" list** for a brand or product manager.

## What it does
1. **Cleans** reviews: flags duplicates, spam-like and too-short text; flags star/text mismatches.
2. **Extracts aspects** (price, quality, delivery, service, battery, sound, comfort, connectivity) clause by clause, so mixed reviews ("great sound but battery drains") are scored correctly. Includes basic Hinglish terms.
3. **Scores sentiment per aspect** (VADER + domain lexicon). Optional LLM extractor in `src/llm_extractor.py`.
4. **Finds concrete issues** by clustering negative clauses (TF-IDF + KMeans) and ranks them with a transparent priority score.
5. **Detects emerging issues** (brand x aspect negative-mention spikes).
6. **Dashboard** (Streamlit): Top 5 fixes with quotes, alerts, aspect sentiment, weekly trends, competitor heatmap, "ask the reviews" search, downloadable PM brief.
7. **Evaluation** against hand-labelled data: per-aspect precision/recall/F1 and Cohen's kappa.

## Supported files
CSV, TSV, TXT (any encoding), Excel (.xlsx), JSON / JSON Lines, Parquet, and gzipped versions. Only a **review text** column is
required; rating, date, brand and title are optional and detected automatically (check them under *Map columns* in the sidebar).
No rating column: ratings are estimated from the text. No date column: trends and emerging alerts are switched off.

## Deeper insights
Topic discovery (any product category), what moves the rating (estimated stars gained by fixing each topic), risk signals
(safety, churn, fraud, refunds), complaints that travel together, words that signal trouble, and an auto-written summary.

## Run it
```bash
pip install -r requirements.txt
python -m src.synth                  # creates sample data (skip if you use real data)
streamlit run app/dashboard.py       # dashboard
python run_pipeline.py               # CLI: writes outputs/brief.md, issues.csv
python -m pytest -q tests            # tests
```

## Use real data
Put a CSV at `data/reviews.csv` (or upload it in the dashboard) with columns:
`review_id, brand, date, rating, review_text`. Public sources: Kaggle product-review datasets
(Amazon, Flipkart). Then edit `ASPECT_TERMS` and `DOMAIN_LEXICON` in `src/config.py` for the category.

## Evaluate properly
```bash
python -m src.evaluate --make-template 250            # sample to hand-label
# each teammate fills pos / neg / none per aspect, in their own copy
python -m src.evaluate --gold rater1.csv --rater2 rater2.csv   # Cohen's kappa
python -m src.evaluate --gold rater1.csv                       # P/R/F1 vs your labels
```
**Important:** the bundled sample data and `labels_gold_synthetic.csv` are synthetic and generated from the same
vocabulary the lexicon knows, so the ~0.99 F1 in `outputs/eval_report.md` only proves the code works. Expect lower
scores on real reviews; report those honestly with an error analysis.

## Priority score
`priority = share of reviews affected x (0.5 + severity) x (1 + recent growth) x (1 + rating drag / 2)`, scaled to 100.

## Structure
```
app/dashboard.py     Streamlit UI          src/pipeline.py   cleaning, aspects, issues, spikes
src/config.py        lexicons, owners      src/evaluate.py   metrics + kappa
src/synth.py         sample data           src/brief.py      PM brief
src/search.py        review search         src/llm_extractor.py  optional LLM upgrade
```

## Known limitations / next steps
- Rule-based aspects miss sarcasm and unseen vocabulary; compare against the LLM extractor and a fine-tuned model.
- Issue clustering is TF-IDF based; upgrade to sentence embeddings or BERTopic.
- Fake-review detection is heuristic only.
- Respect each site's terms of service and privacy rules if you collect data yourself.
