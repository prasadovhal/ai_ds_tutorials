import pandas as pd
import seaborn as sns 
import string
import re
import spacy

from warnings import simplefilter
simplefilter("ignore")

#######################################################################

df = pd.read_csv('train.csv')
df.drop(columns=['Unnamed: 0'], inplace=True)
df.rename(columns={'label':'labels'},inplace=True)
df.dropna(axis=0,inplace=True)

df.duplicated().sum()
df.drop_duplicates(inplace=True)

nlp = spacy.load("en_core_web_sm")

data2 = df.copy()


def clean_text(text):

    text = text.lower()
    text = text.replace('\n', ' ')
    text = re.sub(r'\d+', ' ', text)
    text = text.translate(str.maketrans(' ', ' ', string.punctuation))
    text = re.sub(r'\s+', ' ', text, flags=re.I)
    
    return text
    

data2['title'] = data2['title'].apply(clean_text)
data2.drop(columns=['text'],inplace=True)
data2.rename(columns={'title':'text'},inplace=True)
# news_map = {1:'real',0:'fake'}
# data2['label_names'] = data2['labels'].map(news_map)

data2.dropna(inplace=True)


data2.to_csv('cleaned_data.csv',index=False)



#####################################################################

df = pd.read_csv('train.csv')
df.drop(columns=['Unnamed: 0'], inplace=True)
df.dropna(axis=0,inplace=True)

df.duplicated().sum()
df.drop_duplicates(inplace=True)
df.to_csv('cleaned_data2.csv',index=False)
