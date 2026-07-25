
import json
import re
import pandas as pd


def main():
    genres = pd.read_csv(
        "data/u.genre", sep="|", header=None, names=["genre", "genre_id"]
    ).sort_values("genre_id")["genre"].tolist()

    items = pd.read_csv(
        "data/u.item", sep="|", header=None, encoding="latin-1",
        usecols=[0, 1, *range(5, 24)],
    )

    train = pd.read_csv("data/train.csv")
    item_counts = train["item_id"].value_counts()

    records = {}
    for row in items.itertuples(index=False):
        item_id = int(row[0])
        title = row[1]
        m = re.search(r"\((\d{4})\)", title)
        year = int(m.group(1)) if m else None
        flags = row[2:]
        active = [g for g, f in zip(genres, flags) if f == 1]
        records[item_id] = {
            "title": title, "year": year,
            "genres": active, "n_ratings": int(item_counts.get(item_id, 0)),
        }

    print(records[1])
    print("total:", len(records))

    with open("data/items.json", "w", encoding="utf-8") as handle:
        json.dump(records, handle)


if __name__ == "__main__":
    main()
