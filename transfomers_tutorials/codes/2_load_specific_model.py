from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "bert-base-uncased"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

text = "Transformers are amazing."

inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)
probs = torch.softmax(outputs.logits, dim=1)

print(probs)


"""
1. Tokenizer
    -   Splits text into tokens
    -   Converts tokens → IDs
    -   Adds special tokens [CLS] [SEP]
2. Model
    -   Takes token IDs
    -   Produces logits (raw scores)
3. Softmax
    -   Convert logits → probabilities
"""