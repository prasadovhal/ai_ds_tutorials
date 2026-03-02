import pandas as pd

train = pd.read_csv("train.csv")
test = pd.read_csv("test.csv")

print(train.head())
print(train.info())

train['target'].value_counts(normalize=True)

import seaborn as sns
import matplotlib.pyplot as plt

sns.countplot(x='target', data=train)
plt.show()

train['length'] = train['text'].apply(len)

sns.histplot(train[train['target']==1]['length'], color='red', label='Disaster')
sns.histplot(train[train['target']==0]['length'], color='blue', label='Non-Disaster')
plt.legend()
plt.show()