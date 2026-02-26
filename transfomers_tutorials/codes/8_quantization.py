# load model

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "distilbert-base-uncased-finetuned-sst-2-english"

model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

model.eval()

# quantize model

import torch

torch.backends.quantized.engine = "qnnpack"

quantized_model = torch.quantization.quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)


# check model size

import os
torch.save(model.state_dict(), "fp32.pth")
torch.save(quantized_model.state_dict(), "int8.pth")

print("FP32 size:", os.path.getsize("fp32.pth") / 1e6, "MB")
print("INT8 size:", os.path.getsize("int8.pth") / 1e6, "MB")


# run inference

inputs = tokenizer("I love AI", return_tensors="pt")

with torch.no_grad():
    outputs = quantized_model(**inputs)

print(outputs.logits)