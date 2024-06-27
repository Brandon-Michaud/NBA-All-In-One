import pandas as pd


# Get the number possessions each player played for an entire season
def get_possession_counts_single_season(season, season_type, all_possessions_filename, possession_counts_filename):
    # Get all the possessions for the season
    possessions = pd.read_csv(all_possessions_filename.format(season, season_type), dtype=str)

    # Define the columns names
    offensive_player_columns = [f'offensive_player{i}' for i in range(1, 6)]
    defensive_player_columns = [f'defensive_player{i}' for i in range(1, 6)]

    # Get a list of all the unique player IDs
    player_ids = pd.unique(possessions[offensive_player_columns + defensive_player_columns].values.ravel())
    n_players = len(player_ids)

    # Separate offense and defense
    offensive_possessions = possessions[offensive_player_columns]
    defensive_possessions = possessions[defensive_player_columns]

    # Count the number of possessions for each player
    rows = []
    for i, player_id in enumerate(player_ids):
        print(f'{(i / n_players):.2%} {season} {season_type}: {player_id}')

        # Count the number of possessions
        player_offensive_possessions = offensive_possessions[offensive_possessions.apply(lambda row: player_id in row.values, axis=1)].shape[0]
        player_defensive_possessions = defensive_possessions[defensive_possessions.apply(lambda row: player_id in row.values, axis=1)].shape[0]
        player_total_possessions = player_offensive_possessions + player_defensive_possessions

        # Add possession counts to list for all players
        rows.append([player_id, player_offensive_possessions, player_defensive_possessions, player_total_possessions])

    # Build a dataframe from the list of possession counts
    possession_counts = pd.DataFrame(rows)

    # Rename columns
    possession_counts.columns = ['PLAYER_ID', 'O_POSS', 'D_POSS', 'POSS']

    # Save possession counts to csv
    possession_counts.to_csv(possession_counts_filename.format(season, season_type), index=False)


# Get the number possessions each player played for season-by-season
def get_possession_counts_seasons(seasons, season_types, all_possessions_filename, possession_counts_filename):
    # Loop over every season
    for season in seasons:
        for season_type in season_types:
            get_possession_counts_single_season(season, season_type, all_possessions_filename,
                                                possession_counts_filename)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    all_possessions_filename = '../Data/Possessions/Standard/Seasons/possessions_{}_{}.csv'
    possession_counts_filename = '../Data/SeasonStats/Possessions/{}_{}.csv'
    get_possession_counts_seasons(seasons, season_types, all_possessions_filename, possession_counts_filename)
