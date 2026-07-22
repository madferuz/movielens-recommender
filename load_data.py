import pandas as pd

ratings = pd.read_csv(
	"data/u.data",
	sep="\t",
	header=None,
	names=["user_id", "item_id", "rating", "timestamp"],
)
print(ratings.head())

n_users = ratings["user_id"].nunique()
n_items = ratings["item_id"].nunique()

print(ratings.shape)
print(n_users, n_items)
print(1 - len(ratings) / (n_users * n_items))
print(ratings.rating.value_counts().sort_index())

movies = pd.read_csv(
	"data/u.item",
	sep="|",
	header=None,
	usecols=[0, 1],
	names=["item_id", "title"],
	encoding="latin-1",
)
print(movies.head())
