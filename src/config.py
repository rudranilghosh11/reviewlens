"""Central configuration: aspect lexicon, domain sentiment words, owners and actions."""
import re

# Aspect -> regex fragments (prefix-matched, case-insensitive). Extend per category.
ASPECT_TERMS = {
    "price": ["price", "cost", "expensive", "cheap", "value for money", "worth", "overpriced",
              "overcharged", "paisa vasool", "mehenga", "affordable", "discount"],
    "quality": ["quality", "build", "material", "broke", "broken", "stopped working", "defect",
                "durable", "flimsy", "plastic", "crack", "faulty", "went dead", "snapped",
                "sturdy", "ghatiya"],
    "delivery": ["deliver", "shipping", "shipped", "arrived", "package", "packaging", "courier",
                 "dispatch", "late\\b", "delay", "parcel", "box\\b"],
    "service": ["customer support", "support", "refund", "replacement", "return", "warranty",
                "service cent", "helpline", "agent"],
    "battery": ["battery", "charge", "charging", "backup", "drain"],
    "sound": ["sound", "bass", "audio", "volume", "treble", "noise cancel", "mic\\b"],
    "comfort": ["comfort", "fit\\b", "ear tip", "ache", "ears ", "loose", "heavy", "tight"],
    "connectivity": ["bluetooth", "pairing", "connect", "disconnect", "lag\\b", "latency",
                     "app\\b"],
}
ASPECT_RE = {a: re.compile(r"\b(?:" + "|".join(t) + ")", re.I) for a, t in ASPECT_TERMS.items()}

# Domain words VADER does not know (incl. a few Hinglish terms for Indian e-commerce).
DOMAIN_LEXICON = {
    "late": -1.8, "delayed": -2.0, "damaged": -2.5, "crushed": -2.0, "torn": -1.5, "wrong": -2.0,
    "drains": -2.2, "drain": -2.0, "dead": -2.5, "broke": -2.5, "snapped": -2.0, "stopped": -1.2,
    "flimsy": -2.2, "fragile": -1.5, "cracked": -2.0, "overpriced": -2.5, "expensive": -1.8,
    "overcharged": -2.2, "refused": -2.0, "denied": -2.0, "rejected": -1.8, "ages": -1.8,
    "muffled": -1.8, "muddy": -1.5, "flat": -1.2, "lifeless": -2.0, "quiet": -0.8, "loose": -1.5,
    "ache": -1.8, "disconnecting": -2.0, "drops": -1.3, "fails": -2.0, "nightmare": -3.0,
    "lag": -1.8, "unwatchable": -2.5, "slipping": -1.5, "barely": -1.2, "jumped": -1.0,
    "bekar": -2.5, "ghatiya": -3.0, "mehenga": -2.0,
    "premium": 2.0, "sturdy": 2.0, "durable": 2.0, "quick": 1.5, "prompt": 1.8, "neat": 1.5,
    "polite": 2.0, "fast": 1.5, "crisp": 1.8, "punchy": 1.8, "snug": 1.5, "stable": 1.8,
    "instant": 1.8, "affordable": 1.8, "worth": 1.8, "fairly": 1.0, "solid": 1.5, "resolved": 1.8,
    "approved": 1.8, "lasts": 1.5, "deep": 1.0, "clear": 1.5, "survived": 1.5, "processed": 1.0,
    "answered": 1.0, "smooth": 1.8, "smoothly": 1.8, "hold": 1.0, "fall": -1.2, "falls": -1.2, "badhiya": 2.5, "mast": 2.0, "vasool": 2.5, "soft": 1.2,
}

# Who should act on each aspect, and a default first action.
OWNERS = {"price": "Pricing & Marketing", "quality": "Product & QA", "delivery": "Logistics",
          "service": "Customer Support", "battery": "Hardware / Firmware", "sound": "Product & Audio",
          "comfort": "Design", "connectivity": "Firmware / App"}
ACTIONS = {
    "price": "Review price positioning vs. competitors and test value-led messaging or bundles.",
    "quality": "Open a QA investigation on the failing component and review supplier batches.",
    "delivery": "Audit courier SLAs and packaging; add proactive delay notifications.",
    "service": "Set response/resolution SLAs and simplify refund and warranty workflows.",
    "battery": "Reproduce on current firmware, check recent releases, prepare a patch or advisory.",
    "sound": "Run a tuning review and publish an EQ/mic-setting guide while fixing the root cause.",
    "comfort": "Add more ear-tip sizes in the box and revisit shell ergonomics.",
    "connectivity": "Triage Bluetooth/firmware bug reports and ship a connectivity patch.",
}
