import json
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, RootModel


class RatedItem(BaseModel):
	item_id: int
	rating: float


class RecommendRequest(RootModel[list[RatedItem]]):
	pass


@asynccontextmanager
async def lifespan(app: FastAPI):
	app.state.P = np.load("data/P.npy")
	app.state.Q = np.load("data/Q.npy")
	app.state.bu = np.load("data/bu.npy")
	app.state.bi = np.load("data/bi.npy")

	with open("data/user_map.json", encoding="utf-8") as handle:
		app.state.user_map = {int(key): value for key, value in json.load(handle).items()}

	with open("data/item_map.json", encoding="utf-8") as handle:
		app.state.item_map = {int(key): value for key, value in json.load(handle).items()}

	with open("data/items.json", encoding="utf-8") as handle:
		app.state.items = json.load(handle)

	with open("data/meta.json", encoding="utf-8") as handle:
		app.state.meta = json.load(handle)

	yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:5173"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


@app.get("/genres")
def genres() -> list[str]:
	genre_set = set()
	for item in app.state.items.values():
		genre_set.update(item["genres"])
	return sorted(genre_set)


def _popular_items(limit: int) -> list[dict[str, object]]:
	items = [
		{
			"item_id": int(item_id),
			"title": item["title"],
			"year": item["year"],
			"genres": item["genres"],
			"n_ratings": item["n_ratings"],
		}
		for item_id, item in app.state.items.items()
	]
	items.sort(key=lambda item: item["n_ratings"], reverse=True)
	return items[:limit]


@app.get("/genres/{name}/popular")
def popular_by_genre(name: str, limit: int = 10) -> list[dict[str, object]]:
	items = [
		{
			"item_id": int(item_id),
			"title": item["title"],
			"year": item["year"],
			"genres": item["genres"],
			"n_ratings": item["n_ratings"],
		}
		for item_id, item in app.state.items.items()
		if name in item["genres"]
	]

	items.sort(key=lambda item: item["n_ratings"], reverse=True)
	return items[:limit]


@app.post("/recommend")
def recommend(payload: RecommendRequest, limit: int = 10) -> list[dict[str, object]]:
	lam = 0.1
	k = app.state.Q.shape[1]
	ratings_payload = payload.root

	rated_item_ids = []
	rated_ratings = []
	for rated_item in ratings_payload:
		item_idx = app.state.item_map.get(rated_item.item_id)
		if item_idx is not None:
			rated_item_ids.append(rated_item.item_id)
			rated_ratings.append(rated_item.rating)

	if not rated_item_ids:
		return _popular_items(limit)

	item_indices = np.array([app.state.item_map[item_id] for item_id in rated_item_ids], dtype=np.int64)
	ratings = np.array(rated_ratings, dtype=np.float64)
	Qr = app.state.Q[item_indices]
	resid = ratings - app.state.meta["mu"] - app.state.bi[item_indices]
	A = Qr.T @ Qr + lam * np.eye(k)
	b = Qr.T @ resid
	p_u = np.linalg.solve(A, b)

	scores = app.state.meta["mu"] + app.state.bi + app.state.Q @ p_u
	recommended = []
	rated_set = set(rated_item_ids)

	for item_id_str, item in app.state.items.items():
		item_id = int(item_id_str)
		if item_id in rated_set:
			continue
		item_idx = app.state.item_map.get(item_id)
		if item_idx is None:
			continue
		score = float(scores[item_idx])
		recommended.append(
			{
				"item_id": item_id,
				"title": item["title"],
				"year": item["year"],
				"genres": item["genres"],
				"n_ratings": item["n_ratings"],
				"score": score,
			}
		)

	recommended.sort(key=lambda item: item["score"], reverse=True)
	top_items = recommended[:limit]
	denominator = max(len(top_items) - 1, 1)
	return [
		{
			"item_id": item["item_id"],
			"title": item["title"],
			"year": item["year"],
			"genres": item["genres"],
			"n_ratings": item["n_ratings"],
			"match": float(99 - (29 * index / denominator)),
		}
		for index, item in enumerate(top_items)
	]