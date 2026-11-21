import numpy as np

import pandas as pd
import evaluate
from datasets import Dataset, DatasetDict
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    default_data_collator,
)

SEED = 42
MODEL = "microsoft/deberta-v3-base"
MAX_LENGTH = 512
DATA_CSV = "data/1250_relevance_annotated_posts.csv"  # text_content, relevant
TRAIN_CSV = "data/relevance_train_1000.csv"
TEST_CSV = "data/relevance_test_250.csv"
MODEL_DIR = "data/relevance_classifier_model"
RESULTS_CSV = "data/relevance_classifier_results.csv"
EPOCHS = 10
LEARNING_RATE = 2e-5
TRAIN_BATCH_SIZE = 8
EVAL_BATCH_SIZE = 16
GRAD_ACCUMULATION = 2
WARMUP_RATIO = 0.1


def main() -> None:
    data = pd.read_csv(DATA_CSV).dropna(
        subset=["text_content", "relevant"]).reset_index(drop=True)

    train_idx, test_idx = train_test_split(
        np.arange(len(data)), test_size=0.2, random_state=SEED)
    data.iloc[np.sort(train_idx)].to_csv(TRAIN_CSV, index=False)
    data.iloc[np.sort(test_idx)].to_csv(TEST_CSV, index=False)

    frame = pd.DataFrame({
        "text": data["text_content"],
        "label": data["relevant"].astype(int),
    })
    train_data = frame.iloc[np.sort(train_idx)].reset_index(drop=True)
    test_data = frame.iloc[np.sort(test_idx)].reset_index(drop=True)

    raw_dataset = DatasetDict({
        "train": Dataset.from_pandas(train_data, preserve_index=False),
        "test":  Dataset.from_pandas(test_data,  preserve_index=False),
    })
    print(raw_dataset)
    print(
        f"train positives: {int(train_data.label.sum())} / {len(train_data)}  "
        f"test positives: {int(test_data.label.sum())} / {len(test_data)}"
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL, use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL,
        num_labels=2,
        id2label={0: "IRRELEVANT", 1: "RELEVANT"},
        label2id={"IRRELEVANT": 0, "RELEVANT": 1},
    )

    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            max_length=MAX_LENGTH,
            truncation=True,
        )

    train_dataset = raw_dataset["train"].map(tokenize_function, batched=True)
    eval_dataset  = raw_dataset["test"].map(tokenize_function,  batched=True)

    accuracy  = evaluate.load("accuracy")
    precision = evaluate.load("precision")
    recall    = evaluate.load("recall")
    f1_metric = evaluate.load("f1")

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {
            "accuracy":  accuracy.compute(predictions=preds, references=labels)["accuracy"],
            "precision": precision.compute(predictions=preds, references=labels)["precision"],
            "recall":    recall.compute(predictions=preds, references=labels)["recall"],
            "f1":        f1_metric.compute(predictions=preds, references=labels)["f1"],
        }

    args = TrainingArguments(
        output_dir="checkpoints",
        num_train_epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        warmup_ratio=WARMUP_RATIO,
        eval_strategy="epoch",
        logging_strategy="epoch",
        save_strategy="epoch",
        per_device_train_batch_size=TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=EVAL_BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUMULATION,
        weight_decay=0.01,
        bf16=True,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        seed=SEED,
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=default_data_collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    m = trainer.evaluate()

    trainer.save_model(MODEL_DIR)
    tokenizer.save_pretrained(MODEL_DIR)

    row = {
        "model": MODEL,
        "max_length": MAX_LENGTH,
        "accuracy": round(m["eval_accuracy"], 4),
        "precision": round(m["eval_precision"], 4),
        "recall": round(m["eval_recall"], 4),
        "f1": round(m["eval_f1"], 4),
        "n_test": len(test_data),
    }
    pd.DataFrame([row]).to_csv(RESULTS_CSV, index=False)
    print("\n" + "  ".join(f"{k}={v}" for k, v in row.items()))
    print(f"model -> {MODEL_DIR}    results -> {RESULTS_CSV}")


if __name__ == "__main__":
    main()
