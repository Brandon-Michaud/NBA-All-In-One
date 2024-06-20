import pandas as pd
import os
import time
import pickle
import traceback
from api_helpers import *

# Constants for getting defense data
defense_url = ("https://stats.nba.com/stats/leaguedashptdefend?DateFrom={start_date}&DateTo={end_date}&"
               "DefenseCategory={defense_category}&LastNGames=0&LeagueID=00&Month=0&OpponentTeamID=0&PORound=0&"
               "PerMode={per_mode}&Period=0&Season={season}&SeasonType={season_type}&TeamID=0")
defense_categories = ['Overall', '3 Pointers', '2 Pointers', 'Less Than 6Ft', 'Less Than 10Ft', 'Greater Than 15Ft']


# Get defense stats for a single day
def get_defense_stats_single_day(date, season, season_type, defense_category, save_filename):
    # Format defense stats URL to get stats for date
    url = defense_url.format(start_date=date,
                             end_date=date,
                             per_mode='Totals',
                             defense_category=defense_category,
                             season=season,
                             season_type=season_type)

    # Get the defense stats for this date and save them to csv
    defense_stats = extract_data(url)
    defense_stats.to_csv(save_filename.format(defense_category, season, season_type, date), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get defense stats day-by-day for multiple seasons
def get_defense_stats_every_day(seasons, season_types, schedule_filename, save_filename, fail_filename):
    failed_dates = {}
    for season in seasons:
        for season_type in season_types:
            # Read schedule
            schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

            # Extract the dates from the schedule
            dates = schedule['GAME_DATE'].unique()
            n_dates = len(dates)
            n_defense_categories = len(defense_categories)

            # Get defense stats for each day in schedule
            for i, date in enumerate(dates):
                for j, defense_category in enumerate(defense_categories):
                    print(f'{((i * n_defense_categories + j) / (n_dates * n_defense_categories)):.2%} '
                          f'{season} {season_type}: {date} {defense_category}')
                    try:
                        get_defense_stats_single_day(date, season, season_type, defense_category, save_filename)
                    except Exception as error:
                        print(error)
                        traceback.print_exc()
                        failed_dates[date] = str(error), traceback.format_exc()

        # Save failed dates
        with open(fail_filename, 'wb') as fp:
            pickle.dump(failed_dates, fp)


# Get defense stats for an entire season
def get_defense_stats_whole_season(season, season_type, defense_category, save_filename):
    # Format defense stats URL to get stats for season
    url = defense_url.format(start_date='',
                             end_date='',
                             per_mode='Totals',
                             defense_category=defense_category,
                             season=season,
                             season_type=season_type)

    # Get the defense stats for this season and save them to csv
    defense_stats = extract_data(url)
    defense_stats.to_csv(save_filename.format(defense_category, season, season_type), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get defense stats for entire seasons
def get_defense_stats_seasons(seasons, season_types, save_filename, fail_filename):
    # Keep track of failed seasons
    failed_seasons = {}

    # Constants for finding completion percentage
    n_seasons = len(seasons)
    n_season_types = len(season_types)
    n_defense_categories = len(defense_categories)

    # Get defense stats for each season
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            for k, defense_category in enumerate(defense_categories):
                percent_done = (((i * n_season_types * n_defense_categories) + (j * n_defense_categories) + k) /
                                (n_seasons * n_season_types * n_defense_categories))
                print(f'{percent_done:.2%} {season} {season_type}: {defense_category}')

                # Get defense stats
                try:
                    get_defense_stats_whole_season(season, season_type, defense_category, save_filename)
                except Exception as error:
                    print(error)
                    traceback.print_exc()
                    failed_seasons[f'{season} {season_type} {defense_category}'] = str(error), traceback.format_exc()

    # Save failed seasons
    with open(fail_filename, 'wb') as fp:
        pickle.dump(failed_seasons, fp)


if __name__ == '__main__':
    seasons = range(2013, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    whole_season_save_filename = '../Data/SeasonStats/Defense/{}/{}_{}.csv'
    single_day_save_filename = '../Data/BoxScores/Defense/{}/{}_{}_{}.csv'
    # for defense_category in defense_categories:
    #     os.makedirs(f'../Data/SeasonStats/Defense/{defense_category}', exist_ok=True)
    #     os.makedirs(f'../Data/BoxScores/Defense/{defense_category}', exist_ok=True)
    # get_tracking_stats_every_day(seasons, season_types, schedule_filename, single_day_save_filename, 'Fails/failed_dates.pkl')
    get_defense_stats_seasons(seasons, season_types, whole_season_save_filename, 'Fails/defense.pkl')

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
