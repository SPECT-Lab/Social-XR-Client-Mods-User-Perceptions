import re


import pandas as pd

from labeling_prompts import LABELS

GOLD_CSV = "data/250_multi-label-classifier_evaluation_posts.csv"
GOLD_COL = "manual_labels"
PRED_CSV = "data/labeled_posts.csv"  # from multilabel_classifier.py
PRED_COL = "labels"
PER_LABEL_CSV = "data/evaluation_per_label.csv"
OVERALL_CSV = "data/evaluation_overall.csv"


def load(path, col):
    """record_id -> (label set, text). Text is kept so the join can be verified."""
    df = pd.read_csv(path, usecols=["record_id", col, "text_content"])
    labels = df[col].fillna("").astype(str).apply(
        lambda s: {x.strip() for x in s.split(",") if x.strip()})
    text = df["text_content"].astype(str).apply(
        lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()[:120])
    return dict(zip(df["record_id"], zip(labels, text)))


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def main():
    g, p = load(GOLD_CSV, GOLD_COL), load(PRED_CSV, PRED_COL)
    ids = [i for i in g if i in p]
    missing = len(g) - len(ids)
    if missing:
        print(f"warning: {missing} gold posts have no prediction and are skipped")

    # record_id must refer to the same post in both files, so compare the text.
    bad = [i for i in ids if g[i][1] and p[i][1] and g[i][1] != p[i][1]]
    if bad:
        raise SystemExit(
            f"record_id mismatch: {len(bad)} of {len(ids)} ids point at different posts in\n"
            f"  {GOLD_CSV}\n  {PRED_CSV}\n"
            f"e.g. id {bad[0]}:\n  gold: {g[bad[0]][1][:70]}\n  pred: {p[bad[0]][1][:70]}\n"
            "The two files use different record_id numbering; align them before scoring.")

    gold = {i: g[i][0] for i in ids}
    pred = {i: p[i][0] for i in ids}

    rows = []
    for label in LABELS:
        tp = sum(label in gold[i] and label in pred[i] for i in ids)
        fp = sum(label not in gold[i] and label in pred[i] for i in ids)
        fn = sum(label in gold[i] and label not in pred[i] for i in ids)
        p, r, f = prf(tp, fp, fn)
        rows.append({"label": label, "support": tp + fn, "tp": tp, "fp": fp, "fn": fn,
                     "precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4)})
    per_label = pd.DataFrame(rows)
    per_label.to_csv(PER_LABEL_CSV, index=False)

    tp, fp, fn = per_label.tp.sum(), per_label.fp.sum(), per_label.fn.sum()
    micro = prf(tp, fp, fn)
    seen = per_label[per_label.support > 0]
    macro = tuple(seen[c].mean() for c in ("precision", "recall", "f1"))
    w = seen.support / seen.support.sum()
    weighted = tuple((seen[c] * w).sum() for c in ("precision", "recall", "f1"))
    exact = sum(gold[i] == pred[i] for i in ids) / len(ids)

    overall = pd.DataFrame([
        {"average": a, "precision": round(v[0], 4), "recall": round(v[1], 4), "f1": round(v[2], 4)}
        for a, v in (("micro", micro), ("macro", macro), ("weighted", weighted))
    ])
    overall["n_posts"] = len(ids)
    overall["exact_match"] = round(exact, 4)
    overall.to_csv(OVERALL_CSV, index=False)

    print(per_label.to_string(index=False))
    print()
    print(overall.to_string(index=False))
    print(f"\nper-label -> {PER_LABEL_CSV}    overall -> {OVERALL_CSV}")


if __name__ == "__main__":
    main()
