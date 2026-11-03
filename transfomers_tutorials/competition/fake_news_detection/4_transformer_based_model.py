import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 1️⃣ Load dataset
dataset = load_dataset("csv", data_files={"train": "cleaned_data2.csv"})
dataset = dataset["train"].train_test_split(test_size=0.2)

# 2️⃣ Load tokenizer
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

dataset = dataset.map(tokenize, batched=True)
dataset = dataset.remove_columns(["text"])
dataset.set_format("torch")

# 3️⃣ Load model
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2
).to(device)

"""
to check target_modules to set in PEFT:

for name, module in model.named_modules():
    print(name)
"""
# 4️⃣ Add LoRA
lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_lin", "v_lin"], # as we are using distilbert, the target modules are "q_lin" and "v_lin" instead of "query" and "value"
    # target_modules=["query", "value"],
    # target_modules=["q_proj", "v_proj"], # for some models like LLaMA, the target modules are "q_proj" and "v_proj"
    lora_dropout=0.1,
    bias="none"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# 5️⃣ Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=2,
    eval_strategy="epoch",
    logging_steps=10
)

# 6️⃣ Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
)

trainer.train()

model.save_pretrained("trained_model")
tokenizer.save_pretrained("trained_model")
