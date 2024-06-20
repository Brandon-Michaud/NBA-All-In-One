import pandas as pd
import time
import pickle
import traceback
from api_helpers import *

# Constants for getting general data
general_url = ("https://stats.nba.com/stats/leaguedashplayerstats?DateFrom={start_date}&DateTo={end_date}&LastNGames=0&"
               "LeagueID=00&MeasureType={measure_type}&Month=0&OpponentTeamID=0&PORound=0&PaceAdjust=N&"
               "PerMode={per_mode}&Period=0&PlusMinus=N&Rank=N&Season={season}&SeasonType={season_type}&TeamID=0")
measure_types = ['Base', 'Advanced', 'Misc', 'Scoring', 'Usage', 'Defense']


# Get general stats for a single day
def get_general_stats_single_day(date, season, season_type, measure_type, save_filename):
    # Format general stats URL to get stats for date
    url = general_url.format(start_date=date,
                             end_date=date,
                             per_mode='Totals',
                             measure_type=measure_type,
                             season=season,
                             season_type=season_type)

    # Get the general stats for this date and save them to csv
    general_stats = extract_data(url)
    general_stats.to_csv(save_filename.format(measure_type, season, season_type, date), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get general stats day-by-day for multiple seasons
def get_general_stats_every_day(seasons, season_types, schedule_filename, save_filename, fail_filename):
    failed_dates = {}
    for season in seasons:
        for season_type in season_types:
            # Read schedule
            schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

            # Extract the dates from the schedule
            dates = schedule['GAME_DATE'].unique()
            n_dates = len(dates)
            n_types = len(measure_types)

            # Get general stats for each day in schedule
            for i, date in enumerate(dates):
                for j, measure_type in enumerate(measure_types):
                    print(f'{((i * n_types + j) / (n_dates * n_types)):.2%} {season} {season_type}: {date} {measure_type}')
                    try:
                        get_general_stats_single_day(date, season, season_type, measure_type, save_filename)
                    except Exception as error:
                        print(error)
                        traceback.print_exc()
                        failed_dates[date] = str(error), traceback.format_exc()

        # Save failed dates
        with open(fail_filename, 'wb') as fp:
            pickle.dump(failed_dates, fp)


# Get general stats for an entire season
def get_general_stats_whole_season(season, season_type, measure_type, save_filename):
    # Format general stats URL to get stats for season
    url = general_url.format(start_date='',
                             end_date='',
                             per_mode='PerGame',
                             measure_type=measure_type,
                             season=season,
                             season_type=season_type)

    # Get the general stats for this season and save them to csv
    general_stats = extract_data(url)
    general_stats.to_csv(save_filename.format(measure_type, season, season_type), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get general stats for entire seasons
def get_general_stats_seasons(seasons, season_types, save_filename, fail_filename):
    # Keep track of failed seasons
    failed_seasons = {}

    # Constants for finding completion percentage
    n_seasons = len(seasons)
    n_season_types = len(season_types)
    n_measure_types = len(measure_types)

    # Get general stats for each season
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            for k, measure_type in enumerate(measure_types):
                percent_done = (((i * n_season_types * n_measure_types) + (j * n_measure_types) + k) /
                                (n_seasons * n_season_types * n_measure_types))
                print(f'{percent_done:.2%} {season} {season_type}: {measure_type}')

                # Get general stats
                try:
                    get_general_stats_whole_season(season, season_type, measure_type, save_filename)
                except Exception as error:
                    print(error)
                    traceback.print_exc()
                    failed_seasons[f'{season} {season_type} {measure_type}'] = str(error), traceback.format_exc()

    # Save failed seasons
    with open(fail_filename, 'wb') as fp:
        pickle.dump(failed_seasons, fp)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    whole_season_save_filename = '../Data/SeasonStats/General/{}/{}_{}.csv'
    single_day_save_filename = '../Data/BoxScores/General/{}/{}_{}_{}.csv'
    # get_tracking_stats_every_day(seasons, season_types, schedule_filename, single_day_save_filename, 'Fails/failed_dates.pkl')
    get_general_stats_seasons(seasons, season_types, whole_season_save_filename, 'Fails/general.pkl')

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
