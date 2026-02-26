#🧠 Step 1 — Load Dataset (Small Subset for Demo)

from datasets import load_dataset

dataset = load_dataset("imdb")
small_train = dataset["train"].select(range(500))
small_test = dataset["test"].select(range(200))


#🏗 Step 2 — Load Model & Tokenizer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "bert-base-uncased"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=2
)

# 3 Tokenize dataset
def tokenize_function(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

small_train = small_train.map(tokenize_function, batched=True)
small_test = small_test.map(tokenize_function, batched=True)

small_train = small_train.remove_columns(["text"])
small_test = small_test.remove_columns(["text"])

small_train.set_format("torch")
small_test.set_format("torch")


# 🔹 Step 4 — Add LoRA
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,                  # rank (small number)
    lora_alpha=16,
    target_modules=["query", "value"],  # important!
    lora_dropout=0.1,
)

model = get_peft_model(model, lora_config)

model.print_trainable_parameters()

# 🏁 Step 5 — Train Normally

from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=16,
    num_train_epochs=1,
    eval_strategy="epoch",
)

import evaluate
import numpy as np
accuracy = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=1)
    return accuracy.compute(predictions=predictions, references=labels)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train,
    eval_dataset=small_test,
    compute_metrics=compute_metrics
)

trainer.train()

trainer.evaluate()

########################################################

## QLoRA

from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16",
)

# mps is for apple silicon devices
model = AutoModelForCausalLM.from_pretrained(
    "distilgpt2",
    torch_dtype=torch.float16
).to("mps")

from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["c_attn"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

def tokenize_function(example):
    tokens = tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )
    tokens["labels"] = tokens["input_ids"]
    return tokens

small_train = dataset["train"].select(range(500))
small_test = dataset["test"].select(range(200))
    
small_train = small_train.map(tokenize_function, batched=True)
small_test = small_test.map(tokenize_function, batched=True)

small_train = small_train.remove_columns(["text"])
small_test = small_test.remove_columns(["text"])

small_train.set_format("torch")
small_test.set_format("torch")

#Accuracy per sequence doesn’t mean much. so removed compute_metrics

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train,
    eval_dataset=small_test,
)

trainer.train()

trainer.evaluate()