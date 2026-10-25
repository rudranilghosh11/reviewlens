"""OPTIONAL upgrade: LLM-based aspect + sentiment extraction (handles sarcasm, Hinglish, new aspects).
Needs `pip install anthropic` and ANTHROPIC_API_KEY. Not used by default; compare it against the
rule-based baseline using src/evaluate.py. NOTE: untested without an API key in this repo."""
import json, os

PROMPT = """Extract aspect-level sentiment from this product review. Aspects: price, quality, delivery,
service, battery, sound, comfort, connectivity (add 'other:<name>' for anything else).
Return ONLY JSON: {{"aspects": [{{"aspect": str, "sentiment": "pos|neg|neu", "evidence": str}}]}}
Review: {text}"""

def extract(text, model="claude-haiku-4-5-20251001"):
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(model=model, max_tokens=500,
                                 messages=[{"role": "user", "content": PROMPT.format(text=text)}])
    raw = msg.content[0].text.strip().removeprefix("```json").removesuffix("```").strip()
    try:
        return json.loads(raw)["aspects"]
    except (json.JSONDecodeError, KeyError):
        return []
