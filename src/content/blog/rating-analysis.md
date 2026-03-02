# Modelling CS Matches with Player Performance Distributions
*February 2026 · Analysis*

Using HLTV rating data to model player performance, simulate bo3 draft phases, and estimate expected player ratings for a given matchup.

---

## Background

HLTV's rating system is designed so that 1.0 represents an average performance. Across all professional maps, ratings follow a right-skewed distribution centered just above 1.0. Elite players pull the right tail while the left side is bounded by a natural floor.
<figure style="text-align:center; margin:1em 0;">
    <div id="chart" style="text-align:center;"></div>
    <figcaption style="margin-top:0.5em; font-size:0.9em; color: var(--text);">
      Fig 1. Distribution of HLTV ratings across all players and maps (last 3 months).
    </figcaption>
</figure>
<script>
fetch('/static/img/blog/rating-distribution.svg')
  .then(r => r.text())
  .then(svg => document.getElementById('chart').innerHTML = svg);
</script>

---

## The Log Transform

Applying a log transform centers the distribution at 0, since `log(1) = 0` means average players map exactly to the origin. The result is approximately Gaussian, which makes it straightforward to work with statistically.

```
log(rating) ~ N(μ, σ)
```

<figure style="text-align:center; margin:1em 0;">
  <div id="chart2"></div>
  <figcaption style="margin-top:0.5em; font-size:0.9em; color: var(--text);">
    Fig 2. Log-transformed ratings. The Gaussian fit closely tracks the empirical distribution.
  </figcaption>
</figure>
<script>
fetch('/static/img/blog/log-rating-distribution.svg')
  .then(r => r.text())
  .then(svg => document.getElementById('chart2').innerHTML = svg);
</script>

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

<div id="chart3" style="text-align:center;"></div>
<script>
fetch('/static/img/blog/won-lost-distribution.svg')
  .then(r => r.text())
  .then(svg => document.getElementById('chart3').innerHTML = svg);
</script>

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

## Expected Match Rating

With shrunk parameters in hand, computing a player's expected rating for a given matchup is straightforward. Since ratings are log-normally distributed, the expected rating on a won map is `exp(μ_won + 0.5 · σ_won²)` and similarly for a lost map. In a bo3, each series outcome implies a fixed number of won and lost maps, so the expected rating per outcome is just the weighted average of the two. Integrating over all possible outcomes gives:

```
E[R] = Σ P(outcome) · E[R | outcome]
```

To compute this we need the probability of each series outcome, which depends on team strength and the map draft. We turn to that next.

---

## Team Map Strength

For each team on each map we compute a smoothed win rate using additive smoothing with prior `c = 5` and a dynamic penalty that shrinks as sample size grows:

```
penalty = c / (games + 1)
winrate_smoothed = (wins + c) / (games + 2c + penalty)
```

This pulls win rates toward 0.5 for small sample sizes while applying a slight negative bias for low game counts. The smoothed win rate is then converted to a strength score using a log-odds transformation scaled by K = 400:

```
strength = K · log10(winrate_smoothed / (1 - winrate_smoothed))
```

Teams with no history on a map receive a default strength of -400, acting as a soft permaban in the draft simulation.

---

## Global Team Strength

Map-specific win rates alone do not capture overall team quality. A team with few games on a given map may have misleading strength estimates regardless of smoothing. To address this we incorporate a global team strength prior based on the Valve Regional Standing (VRS) ranking points.

The VRS is an Elo-based system where teams are initially seeded by prize money won and opponent strength, then updated through match results with a recency weighting. A strength difference of 400 points corresponds to a 10x win rate advantage, consistent with our map strength scale. We therefore pass the raw ranking points directly into the Bradley-Terry formula:

```
p_win_global = 1 / (1 + 10^((points_B - points_A) / 400))
```

The final per-map win probability is a weighted blend of the map-specific and global estimates:

```
p_win = 0.7 · p_win_map + 0.3 · p_win_global
```

This gives 70% weight to map-specific performance and 30% to overall team quality, ensuring that teams with strong global form are not penalized purely by sparse map data.

The 70/30 weighting is currently heuristic, chosen to prioritize map-specific information while still anchoring predictions to overall team strength.

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
5. Team 2 bans their worst remaining map
6. Team 1 bans their worst remaining map
7. Remaining map is the decider

The softmax ensures the selection is probabilistic rather than strictly deterministic, capturing the uncertainty in real draft decisions.

Unfortunately, the drafting process is sequential and non-linear, meaning that a closed-form solution for the series win probability is not tractable. The ban–pick decisions depend on previous outcomes and are further randomized via the softmax temperature, introducing path dependence.

As a result, Monte Carlo simulation provides the most practical and robust way to estimate match win probabilities. Running a sufficiently large number of simulations yields an empirical distribution over series outcomes.

This distribution then serves as the foundation for estimating expected player ratings in the head-to-head matchup.

---

## Case Study: Vitality vs MongolZ

Before running the simulation, we compute the per-map strength scores and Bradley-Terry win probabilities for Vitality against MongolZ:

| Map      | Vitality Strength | MongolZ Strength | P(Vitality) |
|----------|-------------------|------------------|-------------|
| Global (VRS)  | 2029         | 1628             | 90.96%      |
| Anubis   | 42.88             | -400.00          | 92.75%      |
| Overpass | 147.69            | -400.00          | 95.90%      |
| Ancient  | -38.76            | -6.10            | 45.31%      |
| Dust2    | 199.72            | -87.08           | 83.90%      |
| Nuke     | 26.78             | -6.10            | 55.96%      |
| Mirage   | 7.39              | 26.30            | 47.28%      |
| Inferno  | 110.37            | -70.44           | 73.90%      |

Vitality are strong favorites on most maps. MongolZ have no history on Anubis and Overpass, receiving the -400 default, effectively removing those maps from contention. Ancient and Mirage are the only maps where MongolZ hold a slight edge.

Running 10 000 Monte Carlo simulations of the full bo3 on map strength alone produces the following outcome distribution:

| Outcome | N    | P      |
|---------|------|--------|
| 2-0     | 4619 | 46.2%  |
| 2-1     | 3404 | 34.0%  |
| 1-2     | 1300 | 13.0%  |
| 0-2     | 677  | 6.8%   |

Adding a global ranking prior (30% weight, based on Valve ranking points) shifts the distribution further toward Vitality:

| Outcome | N    | P      |
|---------|------|--------|
| 2-0     | 5717 | 57.2%  |
| 2-1     | 2969 | 29.7%  |
| 1-2     | 810  | 8.1%   |
| 0-2     | 504  | 5.0%   |

Vitality are heavily favored in both cases, reflecting their dominant form over the last 3 months with 48 won maps against only 7 lost.

---

*More coming soon, stay tuned.*