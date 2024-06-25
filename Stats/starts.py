import pandas as pd

from Possessions.make_possessions import string_to_list


# Convert dictionary to a dataframe
def dictionary_to_rows(dictionary):
    # Create a row for each key-value pair
    rows = []
    for key in dictionary.keys():
        row = [key, dictionary[key]]
        rows.append(row)

    # Convert rows to a dataframe
    df = pd.DataFrame(rows)

    return df


# Find the number of games every player started season-by-season for multiple seasons
def get_games_started_seasons(seasons, season_types, schedule_filename, players_at_period_filename, starts_filename):
    # Loop over seasons and regular season/playoffs
    for season in seasons:
        for season_type in season_types:
            # Read schedule
            schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

            # Extract the game IDs from the schedule
            game_ids = schedule['GAME_ID'].unique()
            n_games = len(game_ids)

            # Store dictionary keeping starts for each player ID
            starts = {}

            # Get possessions for each game
            for i, game_id in enumerate(game_ids):
                print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')

                # Get the starts for the first period
                period_starters = pd.read_csv(players_at_period_filename.format(game_id))
                starters = period_starters.iloc[0]
                starters_player_ids = string_to_list(starters['TEAM_1_PLAYERS'])
                starters_player_ids.extend(string_to_list(starters['TEAM_2_PLAYERS']))

                # Add all starts for each starter
                for starter in starters_player_ids:
                    if starter in starts:
                        starts[starter] += 1
                    else:
                        starts[starter] = 1

            # Convert dictionary to a dataframe
            starts_df = dictionary_to_rows(starts)
            starts_df.columns = ['PLAYER_ID', 'GS']

            # Save starts to csv
            starts_df.to_csv(starts_filename.format(season, season_type), index=False)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    players_at_period_filename = '../Data/PlayersAtPeriod/pap_{}.csv'
    starts_filename = '../Data/SeasonStats/Starts/{}_{}.csv'
    get_games_started_seasons(seasons, season_types, schedule_filename, players_at_period_filename, starts_filename)
