import pandas as pd
from datasets import Dataset

df = pd.read_csv('train.csv')
df.drop(columns=['id', 'input_word_ids', 'input_mask', 'all_segment_id'], inplace=True) 
df.head()

label_columns = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

