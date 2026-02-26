from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
import numpy as np
import evaluate

# 1️⃣ Load dataset
dataset = load_dataset("imdb")

# Use small subset for fast learning
small_train = dataset["train"].select(range(500))
small_test = dataset["test"].select(range(200))

# 2️⃣ Define model name
model_name = "bert-base-uncased"

# 3️⃣ Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 4️⃣ Load model
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2
)

# 5️⃣ Tokenize dataset
def tokenize_function(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

small_train = small_train.map(tokenize_function, batched=True)
small_test = small_test.map(tokenize_function, batched=True)

# Remove raw text column (important)
small_train = small_train.remove_columns(["text"])
small_test = small_test.remove_columns(["text"])

# Set PyTorch format
small_train.set_format("torch")
small_test.set_format("torch")

# 6️⃣ Metrics (optional but recommended)
accuracy = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=1)
    return accuracy.compute(predictions=predictions, references=labels)

# 7️⃣ Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=16,
    num_train_epochs=1,
    logging_steps=10,
    save_strategy="no"  # faster for learning purpose
)

import torch
from torch.utils.data import DataLoader
from torch.optim import AdamW
from transformers import get_scheduler

# Move model to device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Create DataLoader
train_dataloader = DataLoader(
    small_train,
    batch_size=16,
    shuffle=True
)

# Optimizer
optimizer = AdamW(model.parameters(), lr=5e-5)

# Optional: learning rate scheduler
num_epochs = 1
num_training_steps = num_epochs * len(train_dataloader)

lr_scheduler = get_scheduler(
    "linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps
)

# Training loop
model.train()

for epoch in range(1):
    for batch in train_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}

        outputs = model(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
            labels=batch["label"]
        )

        loss = outputs.loss

        if loss is None:
            raise ValueError("Loss is None — labels not passed correctly.")

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()