import pandas as pd
import os
import time
import pickle
import traceback
from api_helpers import *

# Constants for getting shooting data
shooting_url = ("https://stats.nba.com/stats/leaguedashplayershotlocations?DateFrom={start_date}&DateTo={end_date}&"
                "DistanceRange={distance_range}&LastNGames=0&MeasureType={measure_type}&Month=0&OpponentTeamID=0&"
                "PORound=0&PaceAdjust=N&PerMode={per_mode}&Period=0&PlusMinus=N&Rank=N&Season={season}&"
                "SeasonType={season_type}&TeamID=0")
distance_ranges = ['5ft Range', '8ft Range', 'By Zone']
measure_types = ['Base', 'Opponent']


# Get shooting stats for a single day
def get_shooting_stats_single_day(date, season, season_type, distance_range, measure_type, save_filename):
    # Format shooting stats URL to get stats for date
    url = shooting_url.format(start_date=date,
                              end_date=date,
                              per_mode='Totals',
                              distance_range=distance_range,
                              measure_type=measure_type,
                              season=season,
                              season_type=season_type)

    # Get the shooting stats for this date and save them to csv
    shooting_stats = extract_data_two_headers(url)
    shooting_stats.to_csv(save_filename.format(distance_range, season, season_type, measure_type, date), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get shooting stats day-by-day for multiple seasons
def get_shooting_stats_every_day(seasons, season_types, schedule_filename, save_filename, fail_filename):
    failed_dates = {}
    for season in seasons:
        for season_type in season_types:
            # Read schedule
            schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

            # Extract the dates from the schedule
            dates = schedule['GAME_DATE'].unique()
            n_dates = len(dates)
            n_distance_ranges = len(distance_ranges)
            n_measure_types = len(measure_types)

            # Get shooting stats for each day in schedule
            for i, date in enumerate(dates):
                for j, distance_range in enumerate(distance_ranges):
                    for k, measure_type in enumerate(measure_types):
                        print(
                            f'{((i * n_distance_ranges * n_measure_types + j * n_measure_types + k) / (n_dates * n_distance_ranges * n_measure_types)):.2%} '
                            f'{season} {season_type}: {date} {distance_range} {measure_type}')
                        try:
                            get_shooting_stats_single_day(date, season, season_type, distance_range, measure_type,
                                                          save_filename)
                        except Exception as error:
                            print(error)
                            traceback.print_exc()
                            failed_dates[date] = str(error), traceback.format_exc()

        # Save failed dates
        with open(fail_filename, 'wb') as fp:
            pickle.dump(failed_dates, fp)


# Get shooting stats for an entire season
def get_shooting_stats_whole_season(season, season_type, distance_range, measure_type, save_filename):
    # Format shooting stats URL to get stats for season
    url = shooting_url.format(start_date='',
                              end_date='',
                              per_mode='Totals',
                              distance_range=distance_range,
                              measure_type=measure_type,
                              season=season,
                              season_type=season_type)

    # Get the shooting stats for this season and save them to csv
    shooting_stats = extract_data_two_headers(url)
    shooting_stats.to_csv(save_filename.format(distance_range, season, season_type, measure_type), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get shooting stats for entire seasons
def get_shooting_stats_seasons(seasons, season_types, save_filename, fail_filename):
    # Keep track of failed seasons
    failed_seasons = {}

    # Constants for finding completion percentage
    n_seasons = len(seasons)
    n_season_types = len(season_types)
    n_distance_ranges = len(distance_ranges)
    n_measure_types = len(measure_types)

    # Get shooting stats for each season
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            for k, distance_range in enumerate(distance_ranges):
                for l, measure_type in enumerate(measure_types):
                    percent_done = (((i * n_season_types * n_distance_ranges * n_measure_types) + (j * n_distance_ranges * n_measure_types) + (k * n_measure_types) + l) /
                                    (n_seasons * n_season_types * n_distance_ranges * n_measure_types))
                    print(f'{percent_done:.2%} {season} {season_type}: {distance_range} {measure_type}')

                    # Get shooting stats
                    try:
                        get_shooting_stats_whole_season(season, season_type, distance_range, measure_type, save_filename)
                    except Exception as error:
                        print(error)
                        traceback.print_exc()
                        failed_seasons[f'{season} {season_type} {distance_range} {measure_type}'] = str(error), traceback.format_exc()

    # Save failed seasons
    with open(fail_filename, 'wb') as fp:
        pickle.dump(failed_seasons, fp)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    whole_season_save_filename = '../Data/SeasonStats/Shooting/{}/{}_{}_{}.csv'
    single_day_save_filename = '../Data/BoxScores/Shooting/{}/{}_{}_{}_{}.csv'
    # for distance_range in distance_ranges:
    #     os.makedirs(f'../Data/SeasonStats/Shooting/{distance_range}', exist_ok=True)
    #     os.makedirs(f'../Data/BoxScores/Shooting/{distance_range}', exist_ok=True)
    # get_tracking_stats_every_day(seasons, season_types, schedule_filename, single_day_save_filename, 'Fails/failed_dates.pkl')
    get_shooting_stats_seasons(seasons, season_types, whole_season_save_filename, 'Fails/shooting.pkl')

    # with open('Fails/shooting.pkl', 'rb') as fp:
    #     fails = pickle.load(fp)
    #     keys = list(fails.keys())
    #     for key in keys:
    #         key_split = key.split(' ')
    #         season = key_split[0]
    #         if len(key_split) == 6:
    #             season_type = f'{key_split[1]} {key_split[2]}'
    #             distance_range = f'{key_split[3]} {key_split[4]}'
    #             measure_type = key_split[5]
    #         else:
    #             season_type = key_split[1]
    #             distance_range = f'{key_split[2]} {key_split[3]}'
    #             measure_type = key_split[4]
    #
    #         get_shooting_stats_whole_season(season, season_type, distance_range, measure_type,
    #                                         whole_season_save_filename)
