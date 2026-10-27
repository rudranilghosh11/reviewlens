import io
import pandas as pd
from src.ingest import read_csv_robust, guess_columns, standardize

def _cp1252_csv():
    df = pd.DataFrame({"product_name": ["Acme Cooler 1"] * 4, "Rate": ["5", "1", "3", "4"],
                       "Review": ["Great cooling \u02dc loved it", "Delivery was late and box torn", "Okay for the price", "Nice build quality"]})
    return df.to_csv(index=False).encode("cp1252")

def test_reads_windows_encoding_that_utf8_rejects():
    df, enc = read_csv_robust(_cp1252_csv())
    assert enc in ("cp1252", "latin-1") and len(df) == 4

def test_guesses_flipkart_style_columns():
    df, _ = read_csv_robust(_cp1252_csv())
    g = guess_columns(df)
    assert g["review_text"] == "Review" and g["rating"] == "Rate" and g["brand"] == "product_name" and g["date"] is None

def test_standardize_without_dates():
    df, _ = read_csv_robust(_cp1252_csv())
    out, notes = standardize(df, guess_columns(df))
    assert list(out.columns) == ["review_id", "brand", "product", "date", "rating", "review_text"]
    assert any("No date column" in n for n in notes) and out.rating.between(1, 5).all()


def test_reads_json_lines_and_wrapped_json():
    import json
    from src.ingest import read_table
    recs = [{"review_text": "great cooling", "rating": 5}, {"review_text": "loud fan", "rating": 2}]
    assert read_table("\n".join(json.dumps(r) for r in recs).encode(), "x.jsonl")[0].shape == (2, 2)
    assert read_table(json.dumps({"reviews": recs}).encode(), "x.json")[0].shape == (2, 2)

def test_day_first_dates_are_detected():
    from src.ingest import _parse_dates
    out = _parse_dates(pd.Series(["25/12/2025", "03/04/2025"]))
    assert out.iloc[1].month == 4 and out.iloc[0].day == 25

def test_rating_is_optional():
    from src.ingest import standardize
    df = pd.DataFrame({"t": ["I love this, works great"] * 5 + ["Terrible, it broke on day one"] * 5})
    out, notes = standardize(df, {"review_text": "t"})
    assert out.attrs["rating_estimated"] and out.rating.between(1, 5).all()
