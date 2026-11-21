import numpy as np

import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from transformers import AutoModelForSequenceClassification, AutoTokenizer

SEED = 42
DATA_CSV = "data/1250_relevance_annotated_posts.csv"  # text_content, relevant
MODEL_DIR = "data/relevance_classifier_model"
RESULTS_CSV = "data/relevance_classifier_results.csv"
MAX_LENGTH = 512
BATCH_SIZE = 16


def main():
    data = pd.read_csv(DATA_CSV).dropna(
        subset=["text_content", "relevant"]).reset_index(drop=True)

    _, test_idx = train_test_split(
        np.arange(len(data)), test_size=0.2, random_state=SEED)
    test = data.iloc[np.sort(test_idx)]

    texts = test["text_content"].astype(str).tolist()
    labels = test["relevant"].astype(int).to_numpy()
    print(f"test set: {len(test)} posts "
          f"({int(labels.sum())} relevant, {int((labels == 0).sum())} not)")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device).eval()

    preds = []
    with torch.no_grad():
        for i in range(0, len(texts), BATCH_SIZE):
            batch = tokenizer(texts[i:i + BATCH_SIZE], padding="max_length",
                              truncation=True, max_length=MAX_LENGTH,
                              return_tensors="pt").to(device)
            preds.extend(model(**batch).logits.argmax(-1).cpu().tolist())

    preds = np.array(preds)
    tp = int(((preds == 1) & (labels == 1)).sum())
    fp = int(((preds == 1) & (labels == 0)).sum())
    fn = int(((preds == 0) & (labels == 1)).sum())
    tn = int(((preds == 0) & (labels == 0)).sum())

    accuracy = (tp + tn) / len(labels)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0

    row = {
        "model": MODEL_DIR,
        "max_length": MAX_LENGTH,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "n_test": len(test),
    }
    pd.DataFrame([row]).to_csv(RESULTS_CSV, index=False)
    print("\n" + "  ".join(f"{k}={v}" for k, v in row.items()))
    print(f"\n-> {RESULTS_CSV}")


if __name__ == "__main__":
    main()
