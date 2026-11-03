import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer

session = ort.InferenceSession("model_int8.onnx")

tokenizer = AutoTokenizer.from_pretrained("trained_model")

text = "This is fake news!"
inputs = tokenizer(text, return_tensors="np")

outputs = session.run(
    None,
    {
        "input_ids": inputs["input_ids"],
        "attention_mask": inputs["attention_mask"]
    }
)

logits = outputs[0]
prediction = np.argmax(logits, axis=1)

print("Prediction:", prediction)