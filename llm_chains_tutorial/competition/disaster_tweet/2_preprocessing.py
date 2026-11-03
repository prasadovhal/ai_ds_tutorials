import re
import string
import pandas as pd

train = pd.read_csv("train.csv")
test = pd.read_csv("test.csv")

def clean_text(text):
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"@\w+", "", text)
    text = re.sub(r"#", "", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\d+", "", text)
    return text.strip()

train['clean_text'] = train['text'].apply(clean_text)
test['clean_text'] = test['text'].apply(clean_text)

train.to_csv("train_clean.csv", index=False)
test.to_csv("test_clean.csv", index=False)