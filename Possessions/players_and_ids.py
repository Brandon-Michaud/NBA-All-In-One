import pandas as pd


# Get the unique player names and IDs from a single game
def get_players_and_ids_single_game(game_id, play_by_play_filename):
    # Get the play-by-play data
    play_by_play = pd.read_csv(play_by_play_filename.format(game_id))

    # Replace NA values with empty strings
    play_by_play = play_by_play.fillna('')

    # Get team IDs for each player column
    teams1 = play_by_play['PLAYER1_TEAM_ID'][play_by_play['PLAYER1_TEAM_ID'] != ''].unique()
    teams2 = play_by_play['PLAYER2_TEAM_ID'][play_by_play['PLAYER2_TEAM_ID'] != ''].unique()
    teams3 = play_by_play['PLAYER3_TEAM_ID'][play_by_play['PLAYER3_TEAM_ID'] != ''].unique()

    # Combine team IDs from each player column
    teams = {*teams1, *teams2, *teams3}
    teams = sorted(list(teams))

    # Ensure 2 teams were found
    if len(teams) != 2:
        print('Did not find 2 teams')
        print(f'Teams: {teams}')

    # Find the unique players and ids for both teams
    both_team_players = []
    for team in teams:
        # Get the player IDs and names for each player column if they are on the current team
        players1 = play_by_play[['PLAYER1_ID', 'PLAYER1_NAME']][(play_by_play['PLAYER1_TEAM_ID'] == team) &
                                                                (play_by_play['PLAYER1_ID'] != 0)].drop_duplicates()
        players1.columns = ['PLAYER_ID', 'PLAYER_NAME']
        players2 = play_by_play[['PLAYER2_ID', 'PLAYER2_NAME']][(play_by_play['PLAYER2_TEAM_ID'] == team) &
                                                                (play_by_play['PLAYER2_ID'] != 0)].drop_duplicates()
        players2.columns = ['PLAYER_ID', 'PLAYER_NAME']
        players3 = play_by_play[['PLAYER3_ID', 'PLAYER3_NAME']][(play_by_play['PLAYER3_TEAM_ID'] == team) &
                                                                (play_by_play['PLAYER3_ID'] != 0)].drop_duplicates()
        players3.columns = ['PLAYER_ID', 'PLAYER_NAME']

        # Combine the three columns
        players_list = [players1, players2, players3]
        players = pd.concat(players_list).drop_duplicates()

        # Add players to list for both teams
        both_team_players.append(players)

    # Combine players from both teams
    players_df = pd.concat(both_team_players).drop_duplicates()

    return players_df


# Get the unique player names and IDs from multiple seasons
def get_players_and_ids_seasons(seasons, season_types, schedule_filename, play_by_play_filename,
                                players_and_ids_filename):
    # Keep track of all the players and IDs
    all_players = []

    # Loop over seasons and regular season/playoffs
    for season in seasons:
        for season_type in season_types:
            # Read schedule
            schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

            # Extract the game IDs from the schedule
            game_ids = schedule['GAME_ID'].unique()
            n_games = len(game_ids)

            # Find players on the court at the start of each period for each game
            for i, game_id in enumerate(game_ids):
                print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')

                # Get the players and IDs for this game
                players = get_players_and_ids_single_game(game_id, play_by_play_filename)

                # Add this game's players and IDs to list for all games
                all_players.append(players)

    # Combine players and IDs from all games from all seasons
    all_players_df = pd.concat(all_players).drop_duplicates()

    # Sort players and IDs by ID ascending
    all_players_df = all_players_df.sort_values(by='PLAYER_ID', ascending=True)

    # Save players and IDs to csv
    all_players_df.to_csv(players_and_ids_filename, index=False)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    play_by_play_filename = '../Data/PlayByPlay/pbp_{}.csv'
    get_players_and_ids_seasons(seasons, season_types, schedule_filename, play_by_play_filename,
                                '../Data/players_and_ids.csv')

