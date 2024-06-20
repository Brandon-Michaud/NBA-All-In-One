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
    url = playtype_url.format(per_mode='PerGame',
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
                        failed_seasons[f'{season} {season_type} {play_type} defensive'] = str(error), traceback.format_exc()

    # Save failed seasons
    with open(fail_filename, 'wb') as fp:
        pickle.dump(failed_seasons, fp)


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

    # with open('Fails/general.pkl', 'rb') as fp:
    #     fails = pickle.load(fp)
    #     keys = list(fails.keys())
    #     for key in keys:
    #         key_split = key.split(' ')
    #         season = key_split[0]
    #         if len(key_split) == 4:
    #             season_type = f'{key_split[1]} {key_split[2]}'
    #             track_type = key_split[3]
    #         else:
    #             season_type = key_split[1]
    #             track_type = key_split[2]
    #
    #         if track_type != 'Opponent':
    #             print(key)
    #             get_general_stats_whole_season(season, season_type, track_type, whole_season_save_filename)
