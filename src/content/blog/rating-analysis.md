# Modelling CS Matches with Player Performance Distributions
*February 2026 · Analysis*

Using HLTV rating data to model player performance, simulate bo3 draft phases, and estimate expected player ratings for a given matchup.

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

| Metric        | Interpretation                        |
|---------------|---------------------------------------|
| exp(μ)        | Median expected rating                |
| σ             | Consistency, lower is more consistent |
| exp(μ ± 2σ)  | ~95% performance range                |

---

## Won vs Lost Map Splits

Across all players, ratings are higher on won maps than lost maps. Splitting the full dataset by map outcome and fitting separate distributions confirms this clearly.

![Won vs Lost rating distributions](/static/img/blog/won-lost-distribution.png)
*Fig 3. Log-transformed rating distributions split by map outcome across all players. Won maps are centered above 0, lost maps below.*

Both distributions remain approximately Gaussian, which means the log-normal model holds for each outcome separately. This allows us to fit four parameters per player: μ_won, σ_won, μ_lost, σ_lost, and use these as the basis for player predictions.

Conveniently, the log-normal model holds without any additional tweaking.

---

## Shrinkage

The won/lost split leaves us with potential small sample sizes on both sides. To prevent noisy estimates we apply shrinkage, pulling each player's μ toward the global population mean weighted by sample size:

```
μ_shrunk = (n · μ_player + n_prior · μ_global) / (n + n_prior)
```

With n_prior = 30, a player with only 19 lost maps gets pulled roughly 60% toward the global mean, while a player with 56 won maps is only pulled about 35%. The fewer maps a player has, the more their estimate is pulled toward average.

For ZywOo, the effect is most visible on the lost side where the sample is smallest:

| | Games | Raw | Shrunk |
|---| --- |---|---|
| μ_won | 56 | 1.51 | 1.42 |
| μ_lost | 19 | 0.98 | 0.91 |

ZywOo's raw μ_won of 1.51 is a genuine outlier, so shrinkage pulls it down meaningfully. The other Vitality players (ropz, flamez, mezii, apex) show smaller corrections, with the lost side consistently pulled harder due to the lower sample count.

---

## Team Map Strength

For each team on each map we compute a smoothed win rate using additive smoothing with prior `c = 15`:

```
winrate_smoothed = (wins + c) / (games + 2c)
```

This prevents extreme estimates for players with few maps played, pulling the win rate toward 0.5 for small sample sizes. The smoothed win rate is then converted to a strength score using a log-odds transformation scaled by K = 400:

```
strength = K · log(winrate_smoothed / (1 - winrate_smoothed))
```

This is equivalent to an Elo-style rating where a strength difference of 400 corresponds to a 10x win rate advantage. Team strength on a given map is then the sum of the five players' individual strength scores.

---

## Map Win Probabilities

Given the team strength scores per map, the Bradley-Terry model converts the difference into a win probability:

```
p_win = 1 / (1 + 10^((strength_B - strength_A) / K))
```

For maps where a team has no history, a default weak strength score is used as a fallback. This gives us a win probability for Vitality against MongolZ on each active map, which feeds directly into the bo3 simulation.

---

## Bo3 Draft Simulation

The ban and pick phase is simulated using a softmax over the per-map win probabilities with temperature `τ = 0.2`. This introduces some randomness into the draft, reflecting that teams occasionally make unexpected picks and bans. The full bo3 draft follows the standard CS format:

1. Team 1 bans their worst map
2. Team 2 bans their worst map
3. Team 1 picks their best map
4. Team 2 picks their best map
5. Team 1 bans their worst remaining map
6. Team 2 bans their worst remaining map
7. Remaining map is the decider

The softmax ensures the selection is probabilistic rather than strictly deterministic, capturing the uncertainty in real draft decisions.

---

## Case Study: Vitality vs MongolZ

Before running the simulation, we compute the per-map strength scores and Bradley-Terry win probabilities for Vitality against MongolZ:

| Map | Vitality Strength | MongolZ Strength | P(Vitality) |
|-----|-------------------|------------------|-------------|
| Anubis | 31.67 | -400 | 92.31% |
| Overpass | 66.99 | -10.53 | 60.98% |
| Ancient | 0.00 | 17.39 | 47.50% |
| Dust2 | 103.31 | -33.19 | 68.69% | 
| Nuke | 15.80 | 0.00 | 52.27% |
| Mirage | 42.58 | 7.72 | 55.00% |
| Inferno | 43.66 | -26.78 | 60.00% |

Vitality are favorites on most maps, particularly Anubis and Dust2. Ancient is the only map where MongolZ hold an edge, which is reflected in the 47.50% win probability for Vitality. These per-map probabilities feed directly into the draft simulation.

Running 10 000 Monte Carlo simulations of the full bo3 produces the following outcome distribution:

| Outcome | n    | P      |
|---------|------|--------|
| 2-0     | 3877 | 38.8%  |
| 2-1     | 2806  | 28.1%  |
| 1-2     | 1966  | 19.7%  |
| 0-2     | 1351  | 13.5%   |

Vitality are favored, winning in 2-0 in roughly 39% of simulations. However the match is more competitive than the map win probabilities alone suggest, with MongolZ winning in over 33% of simulations.

Using ZywOo's shrunk per-outcome distributions (μ_won = 1.42, μ_lost = 0.91) and weighting by outcome probability gives an expected rating for the series:

| Outcome | E[rating] | P      |
|---------|-----------|--------|
| 2-0     | 1.42      | 38.8%  |
| 2-1     | 1.25      | 28.1%  |
| 1-2     | 1.08      | 19.7%  |
| 0-2     | 0.91      | 13.5%   |

```
E[rating] = 1.237
```

Extending this methodology to all players in the matchup, the expected ratings for Vitality vs MongolZ are as follows:

| Player | Team | E[rating] |
|--------|------|-----------|
| ropz | Vitality | 1.095 |
| flamez | Vitality | 1.130 |
| zywoo | Vitality | 1.237 |
| mezii | Vitality | 1.046 |
| apex | Vitality | 0.952 |
| blitz | MongolZ | 0.932 |
| mzinho | MongolZ | 0.987 |
| techno | MongolZ | 0.946 |
| 910 | MongolZ | 1.043 |
| cobrazera | MongolZ | 0.986 |

Note that the current model does not account for overall team strength beyond map-specific win rates. Adding a global performance prior, such as HLTV ranking points, would improve the win probability estimates and is a planned next step.

---

*More coming soon, stay tuned.*