# MovieLens Recommender

A small MovieLens 100k recommender built with biased matrix factorization on explicit feedback and evaluated with Recall@10.

## What it does

The pipeline is:

1. Load the MovieLens ratings and item metadata.
2. Build a chronological train/test split.
3. Train a biased matrix factorization model with SGD.
4. Evaluate warm users, cold users, and overall Recall@10.

The model uses a global mean plus user and item bias terms:

```text
r_hat_ui = mu + bu + bi + p_u · q_i
```

## Files

- `load_data.py` loads `u.data` and `u.item` and prints basic dataset stats.
- `split.py` creates the temporal train/test split.
- `train.py` trains the factorization model and saves `P.npy`, `Q.npy`, `bu.npy`, and `bi.npy`.
- `evaluate.py` computes Recall@10 for warm users, cold users, and the full test set.

## Data

Download MovieLens 100k and extract it so the files land in `data/`:

	https://files.grouplens.org/datasets/movielens/ml-100k.zip

The pipeline expects `data/u.data` and `data/u.item`. The dataset is gitignored
because it is redistributable and rebuildable.

## Environment

Python 3.12, with `pandas` and `numpy` (see `requirements.txt`).

## How to run

```bash
python load_data.py
python split.py
python train.py
python evaluate.py
```

The training seed is fixed for reproducibility. `train.py` reads `TRAIN_SEED` and defaults to `42` if it is not set.

## Results

Reported metrics are averaged across 5 fixed random seeds (`42` through `46`) so the results are reproducible and the run-to-run variation is visible.

Warm Recall@10 across the five-seed sweep:

- seed 42: `0.045799`
- seed 43: `0.049297`
- seed 44: `0.044611`
- seed 45: `0.042263`
- seed 46: `0.053482`

Summary:

- mean warm Recall@10: `0.047090`
- range: `0.042263..0.053482`
- warm popularity baseline: `0.031755`
- cold Recall@10: `0.075766`
- overall Recall@10: `0.064934`

Rating prediction error at 20 epochs (seed 42):

- train RMSE: `0.846`
- test RMSE: `0.986`

Test RMSE was still decreasing at epoch 20, so the model had not begun to
overfit within this training budget. No hyperparameter search was run.

The cold Recall@10 figure is **not a model result**. The 192 test users with no
training history receive the popularity list as a fallback. It exceeds the warm
score because new accounts tend to rate mainstream films, making them an easier
population to predict - not a better-served one.

For the API demo, `match` is a rank-based percentage within the returned list,
not a calibrated confidence score.

## Limitations

- The catalog ends around 1998, so every recommendation is a pre-1999 film.
- Popularity is computed once from the training split and never updates. A
	production system would recompute it on a rolling window.
- The split is positional rather than by timestamp value, so the boundary
	timestamp appears in both train and test.
- 66 items appear only in the test set. They have no learned factors and can
	never be recommended.
- 192 of 943 users are cold at evaluation time.
- Warm Recall@10 varies by roughly 24% of its mean across seeds, so a single
	run is not a reliable figure.