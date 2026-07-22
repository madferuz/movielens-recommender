import pandas as pd

train = pd.read_csv("data/train.csv")
test = pd.read_csv("data/test.csv")

top10_items = train["item_id"].value_counts().head(10).index
user_items = test.groupby("user_id")["item_id"].apply(set)

recalls = []
for items in user_items:
	recalls.append(len(set(top10_items) & items) / len(items))

print(sum(recalls) / len(recalls))
