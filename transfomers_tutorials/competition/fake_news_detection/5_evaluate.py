import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model = AutoModelForSequenceClassification.from_pretrained("trained_model")
tokenizer = AutoTokenizer.from_pretrained("trained_model")

text = ["Breaking: Scientists discover water on Mars"]

inputs = tokenizer(text, return_tensors="pt")

outputs = model(**inputs)
preds = np.argmax(outputs.logits.detach().numpy(), axis=1)

print("Prediction:", preds)