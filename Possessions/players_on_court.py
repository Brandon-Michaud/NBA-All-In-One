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
    subs = df[[tag, 'PERIOD', 'EVENTNUM', 'time_left']]
    subs['SUB'] = tag
    subs.columns = ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'time_left', 'SUB']
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

    # Ensure five players were found for both teams
    if len(players1) != 5:
        print(f'Players: {players1}')
        raise Exception('Did not find 5 starters')
    elif len(players2) != 5:
        print(f'Players: {players2}')
        raise Exception('Did not find 5 starters')

    return [team1, players1, team2, players2]


# Get the players on the court at the start of each period for each game for each season for each season type
def get_players_on_court_slow(seasons, season_types, schedule_filename, play_by_play_filename, advanced_box_score_url,
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
                print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')

                # Get players on the court at the start of each period for game
                result = get_players_on_court_single_game_slow(game_id, play_by_play_filename, advanced_box_score_url,
                                                               players_on_court_filename)

                # If there was an error, add it to failures dictionary
                if result[0] != 0:
                    failures[game_id] = result[1:]

    # Save failed links
    with open(failed_filename, 'wb') as fp:
        pickle.dump(failures, fp)


# Get the players on the court at the start of each period for a single game
def get_players_on_court_single_game_slow(game_id, play_by_play_filename, advanced_box_score_url,
                                          players_on_court_filename):
    # Read the play-by-play data
    play_by_play = pd.read_csv(play_by_play_filename.format(game_id))

    # Make new column with time remaining in period
    # This is done to handle revisions which have been made after the fact and have event IDs much higher
    play_by_play['time_left'] = play_by_play['PCTIMESTRING'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

    # Get the substitution events from the play-by-play data
    substitutionsOnly = play_by_play[play_by_play['EVENTMSGTYPE'] == 8][
        ['PERIOD', 'EVENTNUM', 'time_left', 'PLAYER1_ID', 'PLAYER2_ID']]

    # Rename substitution columns for easier readability
    substitutionsOnly.columns = ['PERIOD', 'EVENTNUM', 'time_left', 'OUT', 'IN']

    # Split sub-ins and sub-outs into separate data frames
    subs_in = split_subs(substitutionsOnly, 'IN')
    subs_out = split_subs(substitutionsOnly, 'OUT')

    # Recombine subs where sub-ins and sub-outs are now separate rows
    full_subs = pd.concat([subs_out, subs_in], axis=0).reset_index()[
        ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'time_left', 'SUB']]

    # Sort by the event number
    full_subs = full_subs.sort_values(by='EVENTNUM', ascending=True)

    # Get the first substitution of each period for each player
    first_sub_of_period = full_subs.loc[full_subs.groupby(by=['PERIOD', 'PLAYER_ID'])['time_left'].idxmax()]

    # Get player subbed in for each first substitution of each period for each player
    players_subbed_in_at_each_period = first_sub_of_period[first_sub_of_period['SUB'] == 'IN'][
        ['PLAYER_ID', 'PERIOD', 'SUB']]

    # Get each period of the game
    periods = players_subbed_in_at_each_period['PERIOD'].drop_duplicates().values.tolist()

    # Get the players on the court at the start of each period
    rows = []
    for period in periods:
        # Calculate start and end time of period
        start_time = calculate_start_time_of_period(period) + 5
        end_time = calculate_start_time_of_period(period + 1) - 5

        # Get the advanced box score for the period
        try:
            boxscore_players = extract_data(advanced_box_score_url.format(game_id, start_time, end_time))[
                ['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ID']]
        except Exception as error:
            print(f'Error occurred: {error}')
            print(f'Period: {period}')
            traceback.print_exc()
            return -1, period, str(error), traceback.format_exc()

        # Add period column
        boxscore_players['PERIOD'] = period

        # Get the players subbed in for this period
        players_subbed_in_at_period = players_subbed_in_at_each_period[
            players_subbed_in_at_each_period['PERIOD'] == period]

        # Combine the box score with the players subbed in
        joined_players = pd.merge(boxscore_players, players_subbed_in_at_period, on=['PLAYER_ID', 'PERIOD'],
                                  how='left')

        # Get all the players who were not subbed in and thus began the period on the court
        joined_players = joined_players[pd.isnull(joined_players['SUB'])][
            ['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ID', 'PERIOD']]

        # Create row for period
        try:
            row = frame_to_row(joined_players)
        except Exception as error:
            print(f'Error occurred: {error}')
            print(f'Period: {period}')
            return -1, period, str(error)

        # Add period to row
        row.append(period)

        # Add row to list of rows
        rows.append(row)

        # Sleep for 0.75 seconds to stay under the rate limit
        time.sleep(0.75)

    # Convert rows for each period into a data frame
    players_on_court_at_start_of_period = pd.DataFrame(rows)

    # Rename columns
    cols = ['TEAM_ID_1', 'TEAM_1_PLAYERS', 'TEAM_ID_2', 'TEAM_2_PLAYERS', 'PERIOD']
    players_on_court_at_start_of_period.columns = cols

    # Save data frame
    players_on_court_at_start_of_period.to_csv(players_on_court_filename.format(game_id), index=False)

    # Return success code
    return 0,


# Get the players on the court at the start of each period for each game for each season for each season type
def get_players_on_court_fast(seasons, season_types, schedule_filename, play_by_play_filename,
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
                print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')

                # Find players on the court at the start of each period for the game
                result = get_players_on_court_single_game_fast(game_id, play_by_play_filename, players_on_court_filename)

                # If there was an error, add it to failures dictionary
                if result[0] != 0:
                    failures[game_id] = result[1:]

    # Save failed links
    with open(failed_filename, 'wb') as fp:
        pickle.dump(failures, fp)


# Get the players on the court at the start of each period for a single game
def get_players_on_court_single_game_fast(game_id, play_by_play_filename, players_on_court_filename):
    # Get the play-by-play for the game
    play_by_play = pd.read_csv(play_by_play_filename.format(game_id))

    # Remove technical fouls because players on bench can receive them
    play_by_play = play_by_play[~((play_by_play['EVENTMSGTYPE'] == 6) & (play_by_play['EVENTMSGACTIONTYPE'] == 11))]

    # Replace NA values with empty strings
    play_by_play = play_by_play.fillna('')

    # Make new column with time remaining in period
    # This is done to handle revisions which have been made after the fact and have event IDs much higher
    play_by_play['time_left'] = play_by_play['PCTIMESTRING'].apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]))

    # Get the substitution events from the play-by-play data
    substitutionsOnly = play_by_play[play_by_play['EVENTMSGTYPE'] == 8][
        ['PERIOD', 'EVENTNUM', 'time_left', 'PLAYER1_ID', 'PLAYER2_ID']]

    # Rename substitution columns for easier readability
    substitutionsOnly.columns = ['PERIOD', 'EVENTNUM', 'time_left', 'OUT', 'IN']

    # Split sub-ins and sub-outs into separate data frames
    subs_in = split_subs(substitutionsOnly, 'IN')
    subs_out = split_subs(substitutionsOnly, 'OUT')

    # Recombine subs where sub-ins and sub-outs are now separate rows
    full_subs = pd.concat([subs_out, subs_in], axis=0).reset_index()[
        ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'time_left', 'SUB']]

    # Sort by the event number
    full_subs = full_subs.sort_values(by='EVENTNUM', ascending=True)

    # Get the first substitution of each period for each player
    first_sub_of_period = full_subs.loc[full_subs.groupby(by=['PERIOD', 'PLAYER_ID'])['time_left'].idxmax()]

    # Get player subbed in for each first substitution of each period for each player
    players_subbed_in_at_each_period = first_sub_of_period[first_sub_of_period['SUB'] == 'IN'][
        ['PLAYER_ID', 'PERIOD', 'SUB']]

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
        return -1, 'Did not find 2 teams'

    # Find the starters for each period
    periods = play_by_play['PERIOD'].unique()
    rows = []
    for period in periods:
        # Get play-by-play for the period
        period_play_by_play = play_by_play[play_by_play['PERIOD'] == period]

        # Get the players subbed in for this period
        players_subbed_in_at_period = players_subbed_in_at_each_period[
            players_subbed_in_at_each_period['PERIOD'] == period]

        # Find starters for both teams
        row = []
        for team in teams:
            # Add team to row for period
            row.append(int(team))

            # Get the player IDs for each player column if they are on the current team
            players1 = period_play_by_play['PLAYER1_ID'][(period_play_by_play['PLAYER1_TEAM_ID'] == team) &
                                                         (period_play_by_play['PLAYER1_ID'] != 0)]
            players2 = period_play_by_play['PLAYER2_ID'][(period_play_by_play['PLAYER2_TEAM_ID'] == team) &
                                                         (period_play_by_play['PLAYER2_ID'] != 0)]
            players3 = period_play_by_play['PLAYER3_ID'][(period_play_by_play['PLAYER3_TEAM_ID'] == team) &
                                                         (period_play_by_play['PLAYER3_ID'] != 0)]

            # Join the player IDs with the subs for this period
            joined_players1 = pd.merge(players1, players_subbed_in_at_period, left_on=['PLAYER1_ID'],
                                       right_on=['PLAYER_ID'], how='left')
            joined_players2 = pd.merge(players2, players_subbed_in_at_period, left_on=['PLAYER2_ID'],
                                       right_on=['PLAYER_ID'], how='left')
            joined_players3 = pd.merge(players3, players_subbed_in_at_period, left_on=['PLAYER3_ID'],
                                       right_on=['PLAYER_ID'], how='left')

            # Get all the players who were not subbed in and thus began the period on the court
            starters_players1 = joined_players1[pd.isnull(joined_players1['SUB'])]['PLAYER1_ID'].unique()
            starters_players2 = joined_players2[pd.isnull(joined_players2['SUB'])]['PLAYER2_ID'].unique()
            starters_players3 = joined_players3[pd.isnull(joined_players3['SUB'])]['PLAYER3_ID'].unique()

            # Combine starting player IDs from each player column
            players = {*starters_players1, *starters_players2, *starters_players3}
            sorted_players = sorted(list(players))

            # Ensure 5 starters were found
            if len(sorted_players) != 5:
                print('Did not find 5 starters')
                print(f'Players: {sorted_players}')
                print(f'Period: {period}')
                return -1, period, 'Did not find 5 starters'

            # Add players to row
            row.append(sorted_players)

        # Add period to row
        row.append(period)

        # Add row to list of rows
        rows.append(row)

    # Convert rows for each period into a data frame
    players_on_court_at_start_of_period = pd.DataFrame(rows)

    # Rename columns
    cols = ['TEAM_ID_1', 'TEAM_1_PLAYERS', 'TEAM_ID_2', 'TEAM_2_PLAYERS', 'PERIOD']
    players_on_court_at_start_of_period.columns = cols

    # Save data frame
    players_on_court_at_start_of_period.to_csv(players_on_court_filename.format(game_id), index=False)

    # Return success code
    return 0,


# Fix failed games from fast method by using slow method
def fix_fast_failures(original_failures_filename, play_by_play_filename, advanced_box_score_url,
                      players_on_court_filename, new_failures_filename):
    # Open failed games file
    with open(original_failures_filename, 'rb') as fp:
        # Load failed games dictionary
        failed_games = pickle.load(fp)
        keys = list(failed_games.keys())
        n_games = len(keys)

        # Keep track of new failures
        new_failures = {}

        # Try slow method for each failed game
        for i, game_id in enumerate(keys):
            print(f'{((i + 1) / n_games):.2%}: {game_id}')

            # Find players on the court at the start of each period for the game
            result = get_players_on_court_single_game_slow(game_id, play_by_play_filename,
                                                           advanced_box_score_url, players_on_court_filename)

            # If there was an error, add it to failures dictionary
            if result[0] != 0:
                new_failures[game_id] = result[1:]

        # Save failed links
        with open(new_failures_filename, 'wb') as fp2:
            pickle.dump(new_failures, fp2)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    advanced_box_score_url = 'https://stats.nba.com/stats/boxscoretraditionalv2/?gameId={0}&startPeriod=0&endPeriod=14&startRange={1}&endRange={2}&rangeType=2'
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    play_by_play_filename = '../Data/PlayByPlay/pbp_{}.csv'
    players_on_court_filename = '../Data/PlayersAtPeriod/pap_{}.csv'
    get_players_on_court_fast(seasons, season_types, schedule_filename, play_by_play_filename,
                              players_on_court_filename, 'Fails/failed_starters.pkl')
    fix_fast_failures('Fails/failed_starters.pkl', play_by_play_filename, advanced_box_score_url,
                      players_on_court_filename, 'Fails/failed_starters2.pkl')
