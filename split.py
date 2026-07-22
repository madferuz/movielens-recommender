import pandas as pd

ratings = pd.read_csv(
	"data/u.data",
	sep="\t",
	header=None,
	names=["user_id", "item_id", "rating", "timestamp"],
)

ratings = ratings.sort_values("timestamp")
cutoff = int(len(ratings) * 0.8)

train = ratings.iloc[:cutoff]
test = ratings.iloc[cutoff:]

# Keep the split chronological so future interactions never leak into the past.
train.to_csv("data/train.csv", index=False)
test.to_csv("data/test.csv", index=False)

print("train rows:", len(train))
print("train timestamp range:", train["timestamp"].min(), train["timestamp"].max())
print("test rows:", len(test))
print("test timestamp range:", test["timestamp"].min(), test["timestamp"].max())
