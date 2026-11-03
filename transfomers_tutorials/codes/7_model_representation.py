# 🚀 Part 1 — ONNX (Open Neural Network Exchange)

"""
It allows you to:
    - Train in PyTorch
    -   Run inference in C++
    -   Run in Java
    -   Deploy in production microservices
    -   Optimize with ONNX Runtime

onnx onnxruntime
"""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_id = "distilbert-base-uncased-finetuned-sst-2-english"

model = AutoModelForSequenceClassification.from_pretrained(model_id)
tokenizer = AutoTokenizer.from_pretrained(model_id)

model.eval()

dummy_input = tokenizer(
    "Hello world",
    return_tensors="pt"
)

torch.onnx.export(
    model,
    (dummy_input["input_ids"], dummy_input["attention_mask"]),
    "model.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["logits"],
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence"},
        "attention_mask": {0: "batch_size", 1: "sequence"},
        "logits": {0: "batch_size"},
    },
    opset_version=13
)

print("Export complete!")

"""
saves 

model.onnx - Graph structure
model.onnx.data - Large weight tensors

2 files as ONNX has a file size limit (~2GB). makes Memory loading more efficient

"""


## load model back

import onnxruntime as ort

# Create inference session
session = ort.InferenceSession("model.onnx")

print("Model loaded successfully!")

# check how to use loaded model

import numpy as np
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(
    "distilbert-base-uncased-finetuned-sst-2-english"
)

text = "I love AI"

inputs = tokenizer(text, return_tensors="np")

outputs = session.run(
    None,
    {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"]
    }
)

logits = outputs[0]
predicted_class = np.argmax(logits, axis=1)

print("Logits:", logits)
print("Prediction:", predicted_class)


########################################################

# 🚀 Part 2 — GGUF (For LLM Inference)

"""
A quantized model format used by llama.cpp.

llama-cpp-python
"""

from llama_cpp import Llama

llm = Llama(
    model_path="model-q4.gguf",
    n_ctx=512
)

output = llm("Explain AI in simple terms.", max_tokens=50)
print(output["choices"][0]["text"])