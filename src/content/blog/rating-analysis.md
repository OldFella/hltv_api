# Modelling CS Player Performance with Log-Normal Distributions
*24th February 2026 · Analysis*

Using HLTV rating data to build per-player performance distributions, and how these can be used to predict match outcomes.

---

## Background

HLTV's rating system is designed so that 1.0 represents an average performance. Across all professional maps, ratings follow a right-skewed distribution centered just above 1.0. Elite players pull the right tail while the left side is bounded by a natural floor.

![Overall rating distribution](/static/img/blog/rating-distribution.png)
*Fig 1. Distribution of HLTV ratings across all players and maps (last 3 months).*

---

## The Log Transform

Applying a log transform centers the distribution at 0, since `log(1) = 0` means average players map exactly to the origin. The result is approximately Gaussian, which makes it straightforward to work with statistically.

```
log(rating) ~ N(μ, σ)
```

![Log-transformed rating distribution](/static/img/blog/log-rating-distribution.png)
*Fig 2. Log-transformed ratings. The Gaussian fit closely tracks the empirical distribution.*

This means raw HLTV ratings are approximately **log-normally distributed**, a natural result for a ratio-based performance metric.

---

## Per-Player Distributions

For each player we estimate μ and σ from their last 3 months of map ratings (minimum ~50 maps). These two parameters fully describe a player's typical performance level and consistency.

```python
log_ratings = np.log(player_ratings)
mu    = np.mean(log_ratings)   # typical performance
sigma = np.std(log_ratings)    # consistency
```

| Metric        | Interpretation                         |
|---------------|----------------------------------------|
| exp(μ)        | Median expected rating                 |
| σ             | Consistency, lower is more consistent  |
| exp(μ ± 2σ)  | ~95% performance range                 |

---

## Won vs Lost Map Splits

Across all players, ratings are higher on won maps than lost maps. Splitting the full dataset by map outcome and fitting separate distributions confirms this clearly.

![Won vs Lost rating distributions](/static/img/blog/won-lost-distribution.png)
*Fig 3. Log-transformed rating distributions split by map outcome across all players. Won maps are centered above 0, lost maps below.*

Both distributions remain approximately Gaussian, which means the log-normal model holds for each outcome separately. This allows us to fit four parameters per player: μ_won, σ_won, μ_lost, σ_lost, and use these as the basis for player predictions.

Conveniently, the log-normal model holds without any additional tweaking.

---

## Expected Player Rating

Given a win probability for a map, we can estimate a player's expected rating as a weighted average of their won and lost map distributions:

```
E[rating] = p_win · exp(μ_won) + p_lose · exp(μ_lost)
```

For example, a player with a median rating of 1.16 on won maps and 0.90 on lost maps, facing a 60% win probability, yields an expected rating of 1.056.

The per-map win probability is the core input to this model. More on that in a future post.

---

*Match prediction modelling coming soon, stay tuned.*