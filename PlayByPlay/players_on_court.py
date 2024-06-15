import pandas as pd
import traceback
import pickle
import time
from api_helpers import *


# Calculate the time (in tenths of a second) elapsed before the start of a period
def calculate_start_time_of_period(period):
    # If an overtime period has been played
    if period > 5:
        return (720 * 4 + (period - 5) * 300) * 10

    # If only quarters have been played
    else:
        return 720 * (period - 1) * 10


# For each substitution, get only players who were subbed in or subbed out, but not both
def split_subs(df, tag):
    subs = df[[tag, 'PERIOD', 'EVENTNUM']]
    subs['SUB'] = tag
    subs.columns = ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']
    return subs


# Convert dataframe for players on court at start of period into a single row
def frame_to_row(df):
    # Get the teams
    team1 = df['TEAM_ID'].unique()[0]
    team2 = df['TEAM_ID'].unique()[1]

    # Get the players
    players1 = df[df['TEAM_ID'] == team1]['PLAYER_ID'].tolist()
    players1.sort()
    players2 = df[df['TEAM_ID'] == team2]['PLAYER_ID'].tolist()
    players2.sort()

    return [team1, players1, team2, players2]


# Get the players on the court at the start of each period for each game for each season for each season type
def get_players_on_court(seasons, season_types, schedule_filename, play_by_play_filename, advanced_box_score_url,
                         players_on_court_filename, failed_filename):
    # Keep track of failed downloads
    failures = {}

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
                # Read the play-by-play data
                play_by_play = pd.read_csv(play_by_play_filename.format(game_id))

                # Get the substitution events from the play-by-play data
                substitutionsOnly = play_by_play[play_by_play['EVENTMSGTYPE'] == 8][['PERIOD', 'EVENTNUM', 'PLAYER1_ID', 'PLAYER2_ID']]

                # Rename substitution columns for easier readability
                substitutionsOnly.columns = ['PERIOD', 'EVENTNUM', 'OUT', 'IN']

                # Split sub-ins and sub-outs into separate data frames
                subs_in = split_subs(substitutionsOnly, 'IN')
                subs_out = split_subs(substitutionsOnly, 'OUT')

                # Recombine subs where sub-ins and sub-outs are now separate rows
                full_subs = pd.concat([subs_out, subs_in], axis=0).reset_index()[['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']]

                # Get the first substitution of each period for each player
                first_sub_of_period = full_subs.loc[full_subs.groupby(by=['PERIOD', 'PLAYER_ID'])['EVENTNUM'].idxmin()]

                # Get player subbed in for each first substitution of each period for each player
                players_subbed_in_at_each_period = first_sub_of_period[first_sub_of_period['SUB'] == 'IN'][
                    ['PLAYER_ID', 'PERIOD', 'SUB']]

                # Get each period of the game
                periods = players_subbed_in_at_each_period['PERIOD'].drop_duplicates().values.tolist()

                # Get the players on the court at the start of each period
                rows = []
                game_error = False
                for period in periods:
                    print(f'{((i + 1) / n_games):.2%} {period} {season} {season_type}: {game_id}')

                    # Calculate start and end time of period
                    start_time = calculate_start_time_of_period(period) + 5
                    end_time = calculate_start_time_of_period(period + 1) - 5

                    # Get the advanced box score for the period
                    try:
                        boxscore_players = extract_data(advanced_box_score_url.format(game_id, start_time, end_time))[['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ID']]
                    except Exception as error:
                        print(f'Error occurred: {error}')
                        traceback.print_exc()
                        failures[game_id] = (str(error), traceback.format_exc())
                        game_error = True
                        break

                    # Add period column
                    boxscore_players['PERIOD'] = period

                    # Get the players subbed in for this period
                    players_subbed_in_at_period = players_subbed_in_at_each_period[players_subbed_in_at_each_period['PERIOD'] == period]

                    # Combine the box score with the players subbed in
                    joined_players = pd.merge(boxscore_players, players_subbed_in_at_period, on=['PLAYER_ID', 'PERIOD'], how='left')

                    # Get all the players who were not subbed in and thus began the period on the court
                    joined_players = joined_players[pd.isnull(joined_players['SUB'])][['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ID', 'PERIOD']]

                    # Create row for period
                    row = frame_to_row(joined_players)
                    row.append(period)
                    rows.append(row)

                    # Sleep for 0.75 seconds to stay under the rate limit
                    time.sleep(0.75)

                # If there was an error getting the data for one of the periods, do not proceed with saving the game
                if game_error:
                    continue

                # Convert rows for each period into a data frame
                players_on_court_at_start_of_period = pd.DataFrame(rows)

                # Rename columns
                cols = ['TEAM_ID_1', 'TEAM_1_PLAYERS', 'TEAM_ID_2', 'TEAM_2_PLAYERS', 'PERIOD']
                players_on_court_at_start_of_period.columns = cols

                # Save data frame
                players_on_court_at_start_of_period.to_csv(players_on_court_filename.format(game_id), index=False)

    # Save failed links
    with open(failed_filename, 'wb') as fp:
        pickle.dump(failures, fp)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    advanced_box_score_url = 'https://stats.nba.com/stats/boxscoretraditionalv2/?gameId={0}&startPeriod=0&endPeriod=14&startRange={1}&endRange={2}&rangeType=2'
    get_players_on_court(seasons, season_types, '../Data/Schedules/schedule_{}_{}.csv', '../Data/PlayByPlay/pbp_{}.csv',
                         advanced_box_score_url, '../Data/PlayersAtPeriod/pap_{}.csv', 'failed_links3.pkl')
