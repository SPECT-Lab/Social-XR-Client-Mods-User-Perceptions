
import pandas as pd

from labeling_prompts import LABELS

LABELED_CSV = "data/labeled_posts.csv"  # from multilabel_classifier.py
OUTPUT_CSV = "data/prevalence.csv"


def main():
    labels = pd.read_csv(LABELED_CSV, usecols=["labels"])["labels"].fillna("")
    labels = labels.astype(str).apply(
        lambda s: [x.strip() for x in s.split(",") if x.strip()])
    labeled = labels[labels.apply(len) > 0]

    counts = labels.explode().value_counts()
    rows = [{"label": name,
             "posts": int(counts.get(name, 0)),
             "percent": round(100 * counts.get(name, 0) / len(labeled), 1)}
            for name in LABELS]
    df = pd.DataFrame(rows).sort_values("posts", ascending=False)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"{len(labeled):,} labeled posts of {len(labels):,}\n")
    print(df.to_string(index=False))
    print(f"\n-> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
