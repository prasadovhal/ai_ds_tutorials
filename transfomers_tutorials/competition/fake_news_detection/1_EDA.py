import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
from wordcloud import WordCloud

from warnings import simplefilter
simplefilter("ignore")

#######################################################################

df = pd.read_csv('train.csv')
df.drop(columns=['Unnamed: 0'], inplace=True)
df.rename(columns={'label':'labels'},inplace=True)
df.dropna(axis=0,inplace=True)

df.duplicated().sum()
df.drop_duplicates(inplace=True)

news_map = {1:'real',0:'fake'}
df['label_names'] = df['labels'].map(news_map)

sns.histplot(data=df.label_names)
plt.title('Distribution of the Target Classes',fontsize=25)
plt.xlabel('target classes',fontsize=15)
plt.ylabel('count',fontsize=15)
plt.tight_layout()


####################################
# In general one has 1.5 tokens per word on average
title_tokens = df['title'].apply(lambda x: len(x.split())*1.5)
text_tokens  = df['text'].apply(lambda x: len(x.split())*1.5)
####################################

fig,(ax1,ax2) = plt.subplots(ncols=2,figsize=(12,6))

ax1 = sns.histplot(title_tokens,ax=ax1,bins=20)
ax1.set_xlabel('No. of tokens')
ax1.set_title("Title Tokens",fontsize=20)
ax1.set_xlim(0,40)

ax2 = sns.histplot(text_tokens,ax=ax2,bins=200)
ax2.set_xlabel('No. of tokens')
ax2.set_title("Text Tokens",fontsize=20)
ax2.set_xlim(0,3000)

plt.tight_layout()


##########################
fake_title = df.loc[df.labels == 0]['title'].apply(lambda x: len(x.split()))
real_title = df.loc[df.labels == 1]['title'].apply(lambda x: len(x.split()))

df['title_length'] = df['title'].apply(lambda x: len(x.split()))

avg_title = df.groupby('label_names')['title_length'].mean().reset_index(name='avg title length')
##########################

fig,(ax1,ax2,ax3) = plt.subplots(ncols=3,figsize=(12,6))

ax1 = sns.histplot(fake_title,ax=ax1,bins=6)
ax1.set_xlim(0,24)
ax1.set_xlabel('No. of words')
ax1.set_title("No. of Words (Fake News Title)",fontsize=14)

ax2 = sns.histplot(real_title,ax=ax2,bins=15)
ax2.set_xlim(0,30)
ax2.set_xlabel('No. of words')
ax2.set_title("No. of Words (Real News Title)",fontsize=14)

ax3 = sns.barplot(data=avg_title,x='label_names',y='avg title length')
ax3.set_title("Avg No. of Words (Real vs Fake News Titles)",fontsize=12)

plt.tight_layout()

########################################################

text_fake = ' '.join(df.loc[df.labels == 0]['title'])
text_real = ' '.join(df.loc[df.labels == 1]['title'])

wordcloud_fake = WordCloud().generate(text_fake)
wordcloud_real = WordCloud().generate(text_real)

fig, (ax1,ax2) = plt.subplots(ncols=2,figsize=(12,6))

ax1.imshow(wordcloud_fake)
ax1.axis("off")
ax1.set_title("Wordcloud for the Fake News' Titles",fontsize=20)

ax2.imshow(wordcloud_real)
ax2.axis("off")
ax2.set_title("Wordcloud for the 'Real' News' Titles",fontsize=20)

plt.tight_layout()
plt.show()


