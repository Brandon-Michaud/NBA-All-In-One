import pandas as pd


# Coefficients for calculating boxPIPM (https://www.bball-index.com/player-impact-plus-minus/)
box_pipm_coef = {
    'AVG': {
        'Offense': 0.264,
        'Defense': 0.116,
        'Total': 0.380,
    },
    'GS/G': {
        'Offense': 0.266,
        'Defense': 0.549,
        'Total': 0.815,
    },
    'PTS': {
        'Offense': 0.394,
        'Defense': -0.037,
        'Total': 0.357,
    },
    'OREB': {
        'Offense': 0.328,
        'Defense': -0.230,
        'Total': 0.099,
    },
    'DREB': {
        'Offense': 0.051,
        'Defense': 0.239,
        'Total': 0.290,
    },
    'AST': {
        'Offense': 0.375,
        'Defense': 0.033,
        'Total': 0.409,
    },
    'STL': {
        'Offense': 0.263,
        'Defense': 0.857,
        'Total': 1.120,
    },
    'BLK': {
        'Offense': -0.022,
        'Defense': 0.817,
        'Total': 0.795,
    },
    'TO': {
        'Offense': -0.701,
        'Defense': -0.193,
        'Total': -0.894,
    },
    'PF': {
        'Offense': -0.185,
        'Defense': 0.088,
        'Total': -0.097,
    },
    'FTA': {
        'Offense': 0.012,
        'Defense': 0.037,
        'Total': 0.048,
    },
    '2PA': {
        'Offense': -0.260,
        'Defense': -0.047,
        'Total': -0.307,
    },
    '3PA': {
        'Offense': -0.073,
        'Defense': -0.082,
        'Total': -0.155,
    },
    'INTERCEPT': {
        'Offense': -0.092,
        'Defense': -0.041,
        'Total': -0.133,
    },
}


if __name__ == '__main__':
    print()
