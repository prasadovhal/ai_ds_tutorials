import re
import string
import pandas as pd

train = pd.read_csv("train_clean.csv")
test = pd.read_csv("test_clean.csv")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(
    train['clean_text'], train['target'], test_size=0.2, random_state=42
)

vectorizer = TfidfVectorizer(max_features=10000)
X_train_vec = vectorizer.fit_transform(X_train)
X_val_vec = vectorizer.transform(X_val)

model = LogisticRegression()
model.fit(X_train_vec, y_train)

print("Validation Score:", model.score(X_val_vec, y_val))