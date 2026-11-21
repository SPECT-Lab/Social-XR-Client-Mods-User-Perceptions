import numpy as np

import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer

CORPUS_CSV = "data/full_cleaned_dataset.csv"
MODEL_DIR = "data/relevance_classifier_model"
OUTPUT_CSV = "data/client_security_related_posts.csv"
MAX_LENGTH = 512
BATCH_SIZE = 32

ID2LABEL = {0: "IRRELEVANT", 1: "RELEVANT"}


def main():
    df = pd.read_csv(CORPUS_CSV)
    texts = df["text_content"].astype(str).tolist()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device).eval()

    preds = np.empty(len(texts), dtype=np.int64)
    probs = np.empty(len(texts), dtype=np.float32)
    with torch.no_grad():
        for i in tqdm(range(0, len(texts), BATCH_SIZE), unit="batch"):
            batch = tokenizer(texts[i:i + BATCH_SIZE], padding=True, truncation=True,
                              max_length=MAX_LENGTH, return_tensors="pt").to(device)
            p = torch.softmax(model(**batch).logits, dim=-1)
            preds[i:i + BATCH_SIZE] = p.argmax(-1).cpu().numpy()
            probs[i:i + BATCH_SIZE] = p[:, 1].cpu().float().numpy()

    df["pred_label"] = preds
    df["pred_label_name"] = pd.Series(preds).map(ID2LABEL).values
    df["prob_relevant"] = np.round(probs, 4)
    df["is_relevant"] = df["pred_label"] == 1

    relevant = df[df["is_relevant"]]
    relevant.to_csv(OUTPUT_CSV, index=False)
    print(f"{len(relevant):,} relevant / {len(df):,} classified -> {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
