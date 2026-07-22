import json

import numpy as np
import pandas as pd


def load_map(path):
	with open(path, "r", encoding="utf-8") as handle:
		loaded = json.load(handle)
	return {int(key): int(value) for key, value in loaded.items()}


def recall_at_10(recommended_items, truth_items):
	if not truth_items:
		return 0.0
	return len(set(recommended_items) & truth_items) / len(truth_items)


train = pd.read_csv("data/train.csv")
test = pd.read_csv("data/test.csv")
movies = pd.read_csv(
	"data/u.item",
	sep="|",
	header=None,
	usecols=[0, 1],
	names=["item_id", "title"],
	encoding="latin-1",
)

P = np.load("data/P.npy")
Q = np.load("data/Q.npy")
bu = np.load("data/bu.npy")
bi = np.load("data/bi.npy")
mu = train["rating"].mean()

user_map = load_map("data/user_map.json")
item_map = load_map("data/item_map.json")
titles = dict(zip(movies.item_id, movies.title))

known_item_ids = np.array([item_id for item_id, _ in sorted(item_map.items(), key=lambda pair: pair[1])])
train_items_by_user = train.groupby("user_id")["item_id"].apply(set).to_dict()
test_items_by_user = test.groupby("user_id")["item_id"].apply(set).to_dict()
popular_items = train["item_id"].value_counts().head(10).index.tolist()
counts = train["item_id"].value_counts()

warm_recalls = []
cold_recalls = []
warm_popular_recalls = []
all_recalls = []

for user_id, truth_items in test_items_by_user.items():
	if user_id in user_map:
		user_idx = user_map[user_id]
		scores = mu + bu[user_idx] + bi + P[user_idx] @ Q.T
		seen_items = train_items_by_user.get(user_id, set())
		mask = np.ones(len(known_item_ids), dtype=bool)
		for item_id in seen_items:
			item_idx = item_map.get(item_id)
			if item_idx is not None:
				mask[item_idx] = False
		candidate_scores = scores[mask]
		candidate_items = known_item_ids[mask]
		if len(candidate_items) == 0:
			recommended_items = []
		elif len(candidate_items) <= 10:
			top_indices = np.argsort(candidate_scores)[::-1]
			recommended_items = candidate_items[top_indices].tolist()
		else:
			top_k = min(10, len(candidate_items))
			top_indices = np.argpartition(candidate_scores, -top_k)[-top_k:]
			top_indices = top_indices[np.argsort(candidate_scores[top_indices])[::-1]]
			recommended_items = candidate_items[top_indices].tolist()
		warm_recalls.append(recall_at_10(recommended_items, truth_items))
		warm_popular_recalls.append(recall_at_10(popular_items, truth_items))
	else:
		recommended_items = popular_items
		cold_recalls.append(recall_at_10(recommended_items, truth_items))

	all_recalls.append(recall_at_10(recommended_items, truth_items))

print("warm recall@10:", sum(warm_recalls) / len(warm_recalls) if warm_recalls else 0.0)
print("warm popularity recall@10:", sum(warm_popular_recalls) / len(warm_popular_recalls) if warm_popular_recalls else 0.0)
print("cold recall@10:", sum(cold_recalls) / len(cold_recalls) if cold_recalls else 0.0)
print("overall recall@10:", sum(all_recalls) / len(all_recalls) if all_recalls else 0.0)

uid = train.user_id.value_counts().index[0]
u = user_map[uid]
scores = mu + bu[u] + bi + P[u] @ Q.T
seen_items = train_items_by_user.get(uid, set())
mask = np.ones(len(known_item_ids), dtype=bool)
for item_id in seen_items:
	item_idx = item_map.get(item_id)
	if item_idx is not None:
		mask[item_idx] = False
masked_scores = scores[mask]
masked_items = known_item_ids[mask]
top_indices = np.argsort(masked_scores)[::-1][:10]

print(f"most active user: {uid}")
for index in top_indices:
	iid = masked_items[index]
	print(f"{titles[iid][:40]:42} score={masked_scores[index]:.2f}  n_ratings={counts.get(iid, 0)}")