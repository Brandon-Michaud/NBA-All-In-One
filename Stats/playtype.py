import pandas as pd
import os
import time
import pickle
import traceback
from api_helpers import *

# Constants for getting play type data
playtype_url = ("https://stats.nba.com/stats/synergyplaytypes?LeagueID=00&PerMode={per_mode}&PlayType={play_type}&"
                "PlayerOrTeam=P&SeasonType={season_type}&SeasonYear={season}&TypeGrouping={off_def}")
play_types = ['Isolation', 'Transition', 'PRBallHandler', 'PRRollman', 'Postup', 'Spotup', 'Handoff', 'Cut',
              'OffScreen', 'OffRebound', 'Misc']
defenses = [True, False, True, True, True, True, True, False, True, False, False]


# Get play type stats for an entire season
def get_playtype_stats_whole_season(season, season_type, play_type, off_def, save_filename):
    # Format play type stats URL to get stats for season
    url = playtype_url.format(per_mode='Totals',
                              play_type=play_type,
                              season=season,
                              season_type=season_type,
                              off_def=off_def)

    # Get the play type stats for this season and save them to csv
    playtype_stats = extract_data(url)
    playtype_stats.to_csv(save_filename.format(play_type, season, season_type, off_def), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get play type stats for entire seasons
def get_playtype_stats_seasons(seasons, season_types, save_filename, fail_filename):
    # Keep track of failed seasons
    failed_seasons = {}

    # Constants for finding completion percentage
    n_seasons = len(seasons)
    n_season_types = len(season_types)
    n_play_types = len(play_types)

    # Get play type stats for each season
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            play_types_zip = zip(play_types, defenses)
            for k, (play_type, defense) in enumerate(play_types_zip):
                percent_done = (((i * n_season_types * n_play_types) + (j * n_play_types) + k) /
                                (n_seasons * n_season_types * n_play_types))
                print(f'{percent_done:.2%} {season} {season_type}: {play_type}')

                # Get play type offensive stats
                try:
                    get_playtype_stats_whole_season(season, season_type, play_type, 'offensive', save_filename)
                except Exception as error:
                    print(error)
                    traceback.print_exc()
                    failed_seasons[f'{season} {season_type} {play_type} offensive'] = str(error), traceback.format_exc()

                # Get play type defensive stats
                if defense:
                    try:
                        get_playtype_stats_whole_season(season, season_type, play_type, 'defensive', save_filename)
                    except Exception as error:
                        print(error)
                        traceback.print_exc()
                        failed_seasons[f'{season} {season_type} {play_type} defensive'] = str(
                            error), traceback.format_exc()

    # Save failed seasons
    with open(fail_filename, 'wb') as fp:
        pickle.dump(failed_seasons, fp)


# Combine players who played for more than one team for a single dataframe
def combine_multi_team_players(df):
    # Define columns that will be used for weighted average
    weighted_columns = ['PERCENTILE', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT',
                        'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX']

    # Calculate the total number of games played by each player in the season
    df['TOTAL_GP'] = df.groupby(['PLAYER_ID'])['GP'].transform('sum')

    # Computed weighted sum by games played for numerical columns
    for weighted_column in weighted_columns:
        df[f'WEIGHTED_{weighted_column}'] = df[weighted_column] * df['GP'] / df['TOTAL_GP']

    # Group by player and sum the weighted columns
    df_no_duplicates = df.groupby(['PLAYER_ID', 'PLAYER_NAME']).agg(
        TEAM_ID=('TEAM_ID', 'last'),
        TEAM_ABBREVIATION=('TEAM_ABBREVIATION', 'last'),
        TEAM_NAME=('TEAM_NAME', 'last'),
        PLAY_TYPE=('PLAY_TYPE', 'first'),
        TYPE_GROUPING=('TYPE_GROUPING', 'first'),
        TOTAL__GP=('GP', 'sum'),
        **{f'{column}': (f'WEIGHTED_{column}', 'sum') for column in weighted_columns}
    ).reset_index()

    return df_no_duplicates


# Combine players who played for more than one team for every season
def combine_multi_team_players_seasons(seasons, season_types, save_filename):
    # Constants for finding completion percentage
    n_seasons = len(seasons)
    n_season_types = len(season_types)
    n_play_types = len(play_types)

    # Get play type stats for each season
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            play_types_zip = zip(play_types, defenses)
            for k, (play_type, defense) in enumerate(play_types_zip):
                percent_done = (((i * n_season_types * n_play_types) + (j * n_play_types) + k) /
                                (n_seasons * n_season_types * n_play_types))
                print(f'{percent_done:.2%} {season} {season_type}: {play_type}')

                # Load offensive play type stats
                o_playtype_stats = pd.read_csv(save_filename.format(play_type, season, season_type, 'offensive'))

                # Group by player and sum the weighted columns
                o_no_duplicates = combine_multi_team_players(o_playtype_stats)

                # Save data without duplicates
                o_no_duplicates.to_csv(save_filename.format(play_type, season, season_type, 'offensive'), index=False)

                if defense:
                    # Load defense play type stats
                    d_playtype_stats = pd.read_csv(save_filename.format(play_type, season, season_type, 'defensive'))

                    # Group by player and sum the weighted columns
                    d_no_duplicates = combine_multi_team_players(d_playtype_stats)

                    # Save data without duplicates
                    d_no_duplicates.to_csv(save_filename.format(play_type, season, season_type, 'defensive'), index=False)


if __name__ == '__main__':
    seasons = range(2015, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    whole_season_save_filename = '../Data/SeasonStats/PlayTypes/{}/{}_{}_{}.csv'
    # for play_type in play_types:
    #     os.makedirs(f'../Data/SeasonStats/PlayTypes/{play_type}', exist_ok=True)
    #     os.makedirs(f'../Data/BoxScores/PlayTypes/{play_type}', exist_ok=True)
    get_playtype_stats_seasons(seasons, season_types, whole_season_save_filename, 'Fails/playtype.pkl')
    # combine_multi_team_players_seasons(seasons, season_types, whole_season_save_filename)

    # with open('Fails/playtype.pkl', 'rb') as fp:
    #     fails = pickle.load(fp)
    #     keys = list(fails.keys())
    #     for key in keys:
    #         print(key)
    #         key_split = key.split(' ')
    #         season = key_split[0]
    #         if len(key_split) == 5:
    #             season_type = f'{key_split[1]} {key_split[2]}'
    #             play_type = key_split[3]
    #             off_def = key_split[4]
    #         else:
    #             season_type = key_split[1]
    #             play_type = key_split[2]
    #             off_def = key_split[3]
    #
    #         get_playtype_stats_whole_season(season, season_type, play_type, off_def, whole_season_save_filename)
