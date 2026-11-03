import pandas as pd
import torch
from datasets import Dataset, Features, Sequence, Value
from transformers import AutoTokenizer, TrainingArguments, Trainer, AutoModelForSequenceClassification

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

df = pd.read_csv('./competition/Jigsaw_multilingual_toxic/train.csv')
df.drop(columns=['id', 'input_word_ids', 'input_mask', 'all_segment_id'], inplace=True) 

label_columns = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
df["labels"] = df[label_columns].values.tolist()
df.rename(columns={"comment_text": "text"}, inplace=True)

features = Features({
    "text": Value("string"),
    "labels": Sequence(Value("float32")) 
})

dataset = Dataset.from_pandas(df[["text", "labels"]], features=features)
dataset = dataset.train_test_split(test_size=0.2)

def convert_labels(example):
    example["labels"] = [float(x) for x in example["labels"]]
    return example

dataset = dataset.map(convert_labels)

# Tokenization
model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=128
    )

dataset = dataset.map(tokenize, batched=True)
dataset.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "labels"]
)

# load model - multilabel classification

num_labels = len(label_columns)

model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    num_labels=num_labels,
    problem_type="multi_label_classification"
).to(device)

# PEFT - LoRA
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    # target_modules=["q_lin", "v_lin"], # as we are using distilbert, the target modules are "q_lin" and "v_lin" instead of "query" and "value"
    target_modules=["query", "value"],
    # target_modules=["q_proj", "v_proj"], # for some models like LLaMA, the target modules are "q_proj" and "v_proj"
    lora_dropout=0.1,
    bias="none"
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# custom metric for evaluation

import numpy as np
from sklearn.metrics import f1_score

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    probs = 1 / (1 + np.exp(-logits))  # sigmoid
    
    preds = (probs > 0.5).astype(int)
    
    f1_macro = f1_score(labels, preds, average="macro")
    f1_micro = f1_score(labels, preds, average="micro")
    
    return {
        "f1_macro": f1_macro,
        "f1_micro": f1_micro
    }

# Training   

training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    per_device_train_batch_size=32,
    per_device_eval_batch_size=32,
    num_train_epochs=2,
    logging_steps=50,
    save_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["test"],
    compute_metrics=compute_metrics
)

trainer.train()


# evaluation 
results = trainer.evaluate()
print(results)


# inference

text = ["You are horrible and disgusting"]

inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs.to(device))

logits = outputs.logits
probs = torch.sigmoid(logits)

predictions = (probs > 0.5).int()

print("Probabilities:", probs)
print("Predictions:", predictions)


# Save the model

model.save_pretrained("multi_label_model")
tokenizer.save_pretrained("multi_label_model")