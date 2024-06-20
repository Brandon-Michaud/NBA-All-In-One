import pandas as pd
import time
import pickle
import traceback
from api_helpers import *

# Constants for getting hustle data
hustle_url = ("https://stats.nba.com/stats/leaguehustlestatsplayer?DateFrom={start_date}&DateTo={end_date}&"
              "LastNGames=0&LeagueID=00&Month=0&OpponentTeamID=0&PORound=0&PaceAdjust=N&PerMode={per_mode}&PlusMinus=N&"
              "Rank=N&Season={season}&SeasonType={season_type}&TeamID=0")


# Get hustle stats for a single day
def get_hustle_stats_single_day(date, season, season_type, save_filename):
    # Format hustle stats URL to get stats for date
    url = hustle_url.format(start_date=date,
                            end_date=date,
                            per_mode='Totals',
                            season=season,
                            season_type=season_type)

    # Get the hustle stats for this date and save them to csv
    hustle_stats = extract_data(url)
    hustle_stats.to_csv(save_filename.format(season, season_type, date), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get hustle stats day-by-day for multiple seasons
def get_hustle_stats_every_day(seasons, season_types, schedule_filename, save_filename, fail_filename):
    # Keep track of failed dates
    failed_dates = {}

    # Constants for calculating completion percentage
    n_seasons = len(seasons)
    n_season_types = len(season_types)

    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            # Read schedule
            schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

            # Extract the dates from the schedule
            dates = schedule['GAME_DATE'].unique()
            n_dates = len(dates)

            # Get hustle stats for each day in schedule
            for k, date in enumerate(dates):
                percent_done = (((i * n_season_types * n_dates) + (j * n_dates) + k) /
                                (n_seasons * n_season_types * n_dates))
                print(f'{percent_done:.2%} {season} {season_type}: {date}')

                # Get hustle stats
                try:
                    get_hustle_stats_single_day(date, season, season_type, save_filename)
                except Exception as error:
                    print(error)
                    traceback.print_exc()
                    failed_dates[date] = str(error), traceback.format_exc()

        # Save failed seasons
        with open(fail_filename, 'wb') as fp:
            pickle.dump(failed_dates, fp)


# Get hustle stats for an entire season
def get_hustle_stats_whole_season(season, season_type, save_filename):
    # Format hustle stats URL to get stats for season
    url = hustle_url.format(start_date='',
                            end_date='',
                            per_mode='Totals',
                            season=season,
                            season_type=season_type)

    # Get the hustle stats for this season and save them to csv
    hustle_stats = extract_data(url)
    hustle_stats.to_csv(save_filename.format(season, season_type), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get hustle stats for entire seasons
def get_hustle_stats_seasons(seasons, season_types, save_filename, fail_filename):
    # Keep track of failed seasons
    failed_seasons = {}

    # Constants for finding completion percentage
    n_seasons = len(seasons)
    n_season_types = len(season_types)

    # Get hustle stats for each season
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            percent_done = ((i * n_season_types + j) / (n_seasons * n_season_types))
            print(f'{percent_done:.2%} {season} {season_type}')

            # Get hustle stats
            try:
                get_hustle_stats_whole_season(season, season_type, save_filename)
            except Exception as error:
                print(error)
                traceback.print_exc()
                failed_seasons[f'{season} {season_type}'] = str(error), traceback.format_exc()

    # Save failed dates
    with open(fail_filename, 'wb') as fp:
        pickle.dump(failed_seasons, fp)


if __name__ == '__main__':
    seasons = range(2015, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    whole_season_save_filename = '../Data/SeasonStats/Hustle/{}_{}.csv'
    single_day_save_filename = '../Data/BoxScores/Hustle/{}_{}_{}.csv'
    # get_hustle_stats_whole_season('2023-24', 'Regular Season', whole_season_save_filename)
    get_hustle_stats_seasons(seasons, season_types, whole_season_save_filename, 'Fails/hustle.pkl')

    # with open('Fails/failed_seasons.pkl', 'rb') as fp:
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
    #         get_tracking_stats_whole_season(season, season_type, track_type, whole_season_save_filename)
