import numpy as np
import pandas as pd
import json
import os

seed = int(os.environ.get("TRAIN_SEED", "42"))
np.random.seed(seed)

train = pd.read_csv("data/train.csv")
test = pd.read_csv("data/test.csv")
mu = train["rating"].mean()

user_map = {uid: i for i, uid in enumerate(sorted(train.user_id.unique()))}
item_map = {iid: i for i, iid in enumerate(sorted(train.item_id.unique()))}

n_users = len(user_map)
n_items = len(item_map)
k = 50

P = np.random.normal(0, 0.1, (n_users, k))
Q = np.random.normal(0, 0.1, (n_items, k))
bu = np.zeros(n_users)
bi = np.zeros(n_items)

ratings = np.array(
	[
		(user_map[user_id], item_map[item_id], rating)
		for user_id, item_id, rating in train[["user_id", "item_id", "rating"]].to_numpy()
	],
	dtype=np.float64,
)

test_ratings = np.array(
	[
		(user_map[user_id], item_map[item_id], rating)
		for user_id, item_id, rating in test[["user_id", "item_id", "rating"]].to_numpy()
		if user_id in user_map and item_id in item_map
	],
	dtype=np.float64,
)

alpha = 0.01
lam = 0.1
epochs = 20

for epoch in range(epochs):
	squared_error = 0.0
	for user_idx, item_idx, rating in ratings:
		user_idx = int(user_idx)
		item_idx = int(item_idx)
		rating = float(rating)

		p_old = P[user_idx].copy()
		q_old = Q[item_idx].copy()
		bu_old = bu[user_idx]
		bi_old = bi[item_idx]

		prediction = mu + bu_old + bi_old + np.dot(p_old, q_old)
		error = rating - prediction

		P[user_idx] = p_old + alpha * (error * q_old - lam * p_old)
		Q[item_idx] = q_old + alpha * (error * p_old - lam * q_old)
		bu[user_idx] = bu_old + alpha * (error - lam * bu_old)
		bi[item_idx] = bi_old + alpha * (error - lam * bi_old)

		squared_error += error ** 2

	rmse = np.sqrt(squared_error / len(ratings))

	test_squared_error = 0.0
	for user_idx, item_idx, rating in test_ratings:
		user_idx = int(user_idx)
		item_idx = int(item_idx)
		rating = float(rating)

		prediction = mu + bu[user_idx] + bi[item_idx] + np.dot(P[user_idx], Q[item_idx])
		error = rating - prediction
		test_squared_error += error ** 2

	test_rmse = np.sqrt(test_squared_error / len(test_ratings))
	print(f"epoch {epoch + 1}: train_rmse={rmse} test_rmse={test_rmse}")

train_user_idx = ratings[:, 0].astype(int)
train_item_idx = ratings[:, 1].astype(int)
train_scores = mu + bu[train_user_idx] + bi[train_item_idx] + np.sum(
	P[train_user_idx] * Q[train_item_idx],
	axis=1,
)
lo, hi = np.percentile(train_scores, [5, 95])

np.save("data/P.npy", P)
np.save("data/Q.npy", Q)
np.save("data/bu.npy", bu)
np.save("data/bi.npy", bi)

with open("data/meta.json", "w", encoding="utf-8") as handle:
	json.dump({"mu": float(mu), "lo": float(lo), "hi": float(hi)}, handle)

with open("data/user_map.json", "w", encoding="utf-8") as handle:
	json.dump({int(uid): int(index) for uid, index in user_map.items()}, handle)

with open("data/item_map.json", "w", encoding="utf-8") as handle:
	json.dump({int(item_id): int(index) for item_id, index in item_map.items()}, handle)

print(P.shape)
print(Q.shape)
