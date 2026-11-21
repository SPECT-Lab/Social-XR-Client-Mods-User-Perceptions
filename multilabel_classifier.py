import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from google import genai
from google.genai import types
from tqdm import tqdm

from labeling_prompts import LABELS, build_prompt

MODEL = "gemini-3.1-flash-lite-preview"
EXAMPLES_JSON = "data/few_shot_examples.json"
POSTS_CSV = "data/client_security_related_posts.csv"  # from apply_relevance_classifier.py
OUTPUT_CSV = "data/labeled_posts.csv"
MAX_EXAMPLE_CHARS = 600
WORKERS = 12


def example_blocks():
    """Fixed per-label examples: {label: {"positive": [...], "negative": [...]}}."""
    spec = json.load(open(EXAMPLES_JSON, encoding="utf-8"))
    blocks = {}
    for name in LABELS:
        entry = spec.get(name, {})
        lines = ["EXAMPLES (positive and negative for this label):"]
        for text, present in ([(t, "true") for t in entry.get("positive", [])] +
                              [(t, "false") for t in entry.get("negative", [])]):
            lines.append('POST: """%s"""' % str(text)[:MAX_EXAMPLE_CHARS])
            lines.append('ANSWER: {"present": %s}' % present)
        blocks[name] = "\n".join(lines) + "\n"
    return blocks


def ask(client, prompt):
    for attempt in range(5):
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0, response_mime_type="application/json"),
            )
            match = re.search(r"\{.*\}", resp.text or "", re.S)
            if match:
                return bool(json.loads(match.group()).get("present", False))
        except Exception:
            pass
        if attempt < 4:
            time.sleep(min(2 ** attempt, 60))
    return None


def main():
    posts = pd.read_csv(POSTS_CSV)
    blocks = example_blocks()
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    done, cache = {}, OUTPUT_CSV + ".jsonl"
    if os.path.exists(cache):
        for line in open(cache, encoding="utf-8"):
            d = json.loads(line)
            if d["present"] is not None:
                done[(d["record_id"], d["label"])] = d["present"]

    tasks = [(r, name) for r in posts.itertuples() for name in LABELS
             if (r.record_id, name) not in done]

    def run(task):
        row, name = task
        prompt = build_prompt(LABELS[name], row.subreddit, row.post_date,
                              row.text_content, blocks[name])
        return row.record_id, name, ask(client, prompt)

    with open(cache, "a", encoding="utf-8") as fp:
        with ThreadPoolExecutor(WORKERS) as ex:
            for rid, name, present in tqdm(ex.map(run, tasks), total=len(tasks), unit="call"):
                if present is not None:
                    done[(rid, name)] = present
                fp.write(json.dumps({"record_id": rid, "label": name, "present": present}) + "\n")
                fp.flush()

    posts["labels"] = [",".join(n for n in LABELS if done.get((rid, n)))
                       for rid in posts["record_id"]]
    posts.to_csv(OUTPUT_CSV, index=False)
    unresolved = sum(1 for rid in posts["record_id"]
                     for n in LABELS if (rid, n) not in done)
    print(f"Labeled {len(posts):,} posts -> {OUTPUT_CSV}")
    if unresolved:
        print(f"{unresolved:,} calls unresolved after retries; re-run to retry them")


if __name__ == "__main__":
    main()
