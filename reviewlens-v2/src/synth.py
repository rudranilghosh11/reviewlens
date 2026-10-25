"""Synthetic earbud-review generator so the project runs end to end with no download.
Swap in real data (Kaggle / Amazon / Flipkart) by dropping a CSV at data/reviews.csv with columns:
review_id, brand, date, rating, review_text.
Also writes a gold-label file used ONLY to sanity-check the pipeline (synthetic, not human labels)."""
import numpy as np, pandas as pd

NOW = pd.Timestamp("2026-10-05")
ASPECTS = ["price", "quality", "delivery", "service", "battery", "sound", "comfort", "connectivity"]
MENTION_W = dict(zip(ASPECTS, [.35, .5, .4, .25, .45, .5, .3, .3]))

POS = {
 "price": ["Great value for money", "Totally worth the price", "Priced fairly for what it offers", "Very affordable for these features"],
 "quality": ["Build quality feels premium", "Solid material and sturdy finish", "Very durable, survived a few drops"],
 "delivery": ["Delivery was quick and the packaging was neat", "Arrived a day before the promised date", "Courier was prompt and the parcel was well packed"],
 "service": ["Customer support resolved my query quickly", "Replacement was approved without any fuss", "Support agent was polite and helpful"],
 "battery": ["Battery easily lasts a full day", "Charging is fast and the backup is excellent", "Battery life is impressive"],
 "sound": ["Sound is crisp with deep bass", "Bass is punchy and the sound is clear", "Sound badhiya hai, bass bhi mast"],
 "comfort": ["Very comfortable even after hours", "The fit is snug and secure while running", "Ear tips feel soft and light"],
 "connectivity": ["Bluetooth pairing is instant", "Connection is stable with zero lag", "Connects to the app without any issue"],
}
NEG = {  # each aspect -> list of sub-themes -> variants
 "price": [["Overpriced for what you get", "Too expensive for the features offered"], ["Price jumped after the sale ended", "Got it cheaper elsewhere, felt overcharged"]],
 "quality": [["Right earbud stopped working after two weeks", "One side went dead within a month"], ["The plastic feels flimsy and cracked easily", "Build feels flimsy and fragile"], ["Case hinge broke within a month", "Case lid snapped off on day twenty"]],
 "delivery": [["Delivery was late by over a week", "Parcel was delayed again and again", "Delivery bahut late thi, bekar experience"], ["Package arrived damaged with the box torn", "Packaging was crushed and the seal was open"], ["Wrong item was delivered", "Delivered the wrong colour"]],
 "service": [["Customer support took ages to reply", "Support never answered my emails"], ["Refund still not processed after three weeks", "Return request was rejected without reason"], ["Service centre refused the warranty replacement", "Warranty claim was denied twice"]],
 "battery": [["Battery drains within two hours", "Battery backup is terrible"], ["Charging case does not hold charge", "Case barely charges the buds even once"]],
 "sound": [["Bass is weak and muddy", "Sound is flat and lifeless"], ["Mic is poor, people cannot hear me", "Mic sounds muffled for callers"], ["Volume is too low even at maximum", "Sound is too quiet outdoors"]],
 "comfort": [["Ear tips hurt after an hour", "Ears ache after long use"], ["Fit is loose and they fall out while running", "Too loose, keeps slipping out"]],
 "connectivity": [["Bluetooth keeps disconnecting", "Connection drops every few minutes"], ["Pairing fails every other day", "Pairing is a nightmare each time"], ["Video lag makes watching unwatchable", "Noticeable lag while gaming"]],
}
FIRMWARE_ISSUE = ["Battery drains fast after the latest firmware update", "Battery backup dropped badly after the update"]
FILLER_A = ["Been using these for commuting.", "Picked this up during the festive sale.", "Third pair of earbuds I have owned.", "Using them mostly for work and music.", "Honest review after a few weeks.", "Bought these for the gym.", ""]
FILLER_B = ["Overall my experience is as above.", "Just sharing my experience.", "Would like others to know this.", "That is all from me.", ""]
# brand -> aspect -> probability that a mention is negative
P_NEG = {
 "Zenbuds": {"price": .08, "service": .55},
 "SonicPeak": {"delivery": .6, "quality": .15},
 "AuraTune": {"comfort": .5, "connectivity": .35},
}

def generate(n=3200, seed=42):
    rng = np.random.default_rng(seed)
    brands = list(P_NEG)
    rows, gold = [], []
    for i in range(n):
        brand = brands[rng.integers(len(brands))]
        date = NOW - pd.Timedelta(days=float(rng.uniform(0, 180)))
        recent_fw = brand == "Zenbuds" and (NOW - date).days <= 35
        w = {a: MENTION_W[a] * (3.0 if (recent_fw and a == "battery") else 1) for a in ASPECTS}
        p = np.array(list(w.values())); p /= p.sum()
        chosen = rng.choice(ASPECTS, size=rng.integers(1, 4), replace=False, p=p)
        sents, labels = [], {a: "none" for a in ASPECTS}
        for a in chosen:
            pn = P_NEG[brand].get(a, .2)
            if recent_fw and a == "battery": pn = .85
            if rng.random() < pn:
                labels[a] = "neg"
                s = rng.choice(FIRMWARE_ISSUE) if (recent_fw and a == "battery" and rng.random() < .7) else \
                    rng.choice(NEG[a][rng.integers(len(NEG[a]))])
            else:
                labels[a] = "pos"; s = rng.choice(POS[a])
            sents.append(s)
        text = " ".join(filter(None, [rng.choice(FILLER_A), f"Using it for {rng.integers(2, 60)} days now."] +
               [s + rng.choice([".", ".", "!"]) for s in sents] + [rng.choice(FILLER_B)]))
        neg_n = sum(v == "neg" for v in labels.values()); pos_n = sum(v == "pos" for v in labels.values())
        rating = int(np.clip(round(4.5 - 1.4 * neg_n + 0.2 * pos_n + rng.normal(0, .45)), 1, 5))
        if rng.random() < .02: rating = 6 - rating  # star/text mismatch
        rows.append(dict(review_id=f"R{i:05d}", brand=brand, product_category="earbuds",
                         date=date.normalize(), rating=rating, review_text=text))
        gold.append(dict(review_id=f"R{i:05d}", **labels))
    df, g = pd.DataFrame(rows), pd.DataFrame(gold)
    # inject ~3% spam / duplicates
    for k in rng.choice(n, size=int(n * .03), replace=False):
        kind = rng.integers(3)
        df.loc[k, "review_text"] = ["Good product good product good product good product good product",
                                    "ok", df.loc[rng.integers(n), "review_text"]][kind]
        g.loc[k, ASPECTS] = "none"
    return df, g

if __name__ == "__main__":
    d, g = generate()
    d.to_csv("data/reviews.csv", index=False); g.to_csv("data/labels_gold_synthetic.csv", index=False)
    print(len(d), "reviews written to data/reviews.csv")
