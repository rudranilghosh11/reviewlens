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
    assert list(out.columns) == ["review_id", "brand", "date", "rating", "review_text"]
    assert any("No date column" in n for n in notes) and out.rating.between(1, 5).all()
