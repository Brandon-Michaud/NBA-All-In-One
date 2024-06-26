import pandas as pd


# Reformat a single game possessions to fit style of RAPM calculator
def reformat_single_game_possessions(game_possessions, date):
    # Reformat each row at a time
    reformatted_possessions = []
    for _, possession in game_possessions.iterrows():
        # Find the offensive and defensive players
        if possession['possession_team'] == possession['team1_id']:
            offensive_players = [possession['team1_player1'], possession['team1_player2'],
                                 possession['team1_player3'], possession['team1_player4'],
                                 possession['team1_player5']]
            defensive_players = [possession['team2_player1'], possession['team2_player2'],
                                 possession['team2_player3'], possession['team2_player4'],
                                 possession['team2_player5']]
            offensive_points = possession['team1_points']
        else:
            offensive_players = [possession['team2_player1'], possession['team2_player2'],
                                 possession['team2_player3'], possession['team2_player4'],
                                 possession['team2_player5']]
            defensive_players = [possession['team1_player1'], possession['team1_player2'],
                                 possession['team1_player3'], possession['team1_player4'],
                                 possession['team1_player5']]
            offensive_points = possession['team2_points']

        # Create a row with offensive players, defensive players, points score in possessions, and number of possessions
        # which is always 1 since we are using possession data instead of stints
        reformatted_possessions.append(offensive_players + defensive_players + [offensive_points, 1, date])

    # Create a data frame with the reformatted possessions
    reformatted_possessions_df = pd.DataFrame(reformatted_possessions)
    reformatted_possessions_df.columns = ['offensive_player1', 'offensive_player2', 'offensive_player3',
                                          'offensive_player4', 'offensive_player5',
                                          'defensive_player1', 'defensive_player2', 'defensive_player3',
                                          'defensive_player4', 'defensive_player5',
                                          'points', 'possessions', 'date']

    return reformatted_possessions_df


# Combine possessions for a single season
def combine_season_possessions(season, season_type, schedule_filename, possessions_filename,
                               season_possessions_filename):
    # Read schedule
    schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

    # Extract the game IDs from the schedule
    games = schedule[['GAME_ID', 'GAME_DATE']].drop_duplicates()
    games.reset_index(drop=True, inplace=True)
    n_games = games.shape[0]

    # Get possessions for each game in the season
    season_possessions = []
    for i, game in games.iterrows():
        game_id = game['GAME_ID']
        game_date = game['GAME_DATE']
        print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')

        # Get the possessions for this game
        game_possessions = pd.read_csv(possessions_filename.format(game_id))

        # Reformat the possessions
        reformatted_possessions = reformat_single_game_possessions(game_possessions, game_date)

        # Add this game's reformatted possessions to season-long list
        season_possessions.append(reformatted_possessions)

    # Combine reformatted possessions for every game in the season
    season_possessions_df = pd.concat(season_possessions)

    # Save season-long possessions to csv
    season_possessions_df.to_csv(season_possessions_filename.format(season, season_type), index=False)


# Combine possessions for multiple seasons
def combine_multiple_season_possessions(seasons, season_types, schedule_filename, possessions_filename,
                                        season_possessions_filename):
    # Loop over seasons and regular season/playoffs
    for season in seasons:
        for season_type in season_types:
            # Combine possessions for this season
            combine_season_possessions(season, season_type, schedule_filename, possessions_filename,
                                       season_possessions_filename)


# Combine all possessions for all seasons
def combine_all_seasons_possessions(seasons, season_types, season_possessions_filename, all_possessions_filename):
    # Loop over seasons and regular season/playoffs
    all_possessions = []
    for season in seasons:
        for season_type in season_types:
            # Load possessions for this season
            possessions = pd.read_csv(season_possessions_filename.format(season, season_type))

            # Add columns for the season and season type
            possessions['season'] = season
            possessions['season_type'] = season_type

            # Add this season's possessions to list of all seasons
            all_possessions.append(possessions)

    # Combine possessions from all seasons
    all_possessions_df = pd.concat(all_possessions)

    # Save all possessions to csv
    all_possessions_df.to_csv(all_possessions_filename, index=False)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    possessions_filename = '../Data/Possessions/LuckAdjusted/Games/possessions_{}.csv'
    season_possessions_filename = '../Data/Possessions/LuckAdjusted/Seasons/possessions_{}_{}.csv'
    all_possessions_filename = '../Data/Possessions/LuckAdjusted/possessions_all.csv'
    # combine_multiple_season_possessions(seasons, season_types, schedule_filename, possessions_filename,
    #                                     season_possessions_filename)
    combine_all_seasons_possessions(seasons, season_types, season_possessions_filename, all_possessions_filename)
