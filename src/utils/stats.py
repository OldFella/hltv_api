import numpy as np
# --- Strength ---

def strength_maps(n_wins, n_games, c=5, K=400):
    """
    Compute Bradley-Terry strength scores from map win/loss records.
    Applies additive smoothing to handle small sample sizes, pulling
    win rates toward 0.5 for teams with few games played.
    Teams with 0 games played are assigned a strength of 0 (neutral).
    
    Args:
        n_wins (np.array): Number of wins per map
        n_games (np.array): Number of games played per map
        c (int): Smoothing prior. Higher c pulls win rate harder toward 0.5
        K (int): Elo scale factor. Strength difference of K = 10x win rate advantage
    Returns:
        np.array: Strength scores per map
    """
    penalty = c / (n_games + 1)

    p_smoothed = (n_wins+ c)/(n_games + ((2* c) + penalty)) 
    
    strength = K * np.log10(p_smoothed/(1-p_smoothed))
    strength[n_games == 0] = -400
    
    return strength

def strength_ranking(points, K=400):
    """
    Convert HLTV ranking points to a Bradley-Terry strength value.
    Uses log scale since ranking points are not on an Elo scale.
    
    Args:
        points (float): HLTV ranking points
        K (int): Elo scale factor
    Returns:
        float: Strength score
    """
    return (points / 1000) * K


def bradley_terry(R_i, R_j, base=10, K=400):
    return 1/(1+base**((R_j - R_i)/K))