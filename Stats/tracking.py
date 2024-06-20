import pandas as pd
import time
import pickle
import traceback
from api_helpers import *

# Constants for getting tracking data
track_url = ("https://stats.nba.com/stats/leaguedashptstats?DateFrom={start_date}&DateTo={end_date}&LastNGames=0&"
             "LeagueID=00&Month=0&OpponentTeamID=0&PORound=0&PerMode={per_mode}&PlayerOrTeam=Player&"
             "PtMeasureType={track_type}&Season={season}&SeasonType={season_type}&TeamID=0")
track_types = ['CatchShoot', 'Drives', 'Defense', 'Passing', 'Possessions', 'PullUpShot', 'Rebounding', 'Efficiency',
               'SpeedDistance', 'ElbowTouch', 'PostTouch', 'PaintTouch']


# Get tracking stats for a single day
def get_tracking_stats_single_day(date, season, season_type, track_type, save_filename):
    # Format tracking stats URL to get stats for date
    url = track_url.format(start_date=date,
                           end_date=date,
                           per_mode='Totals',
                           track_type=track_type,
                           season=season,
                           season_type=season_type)

    # Get the tracking stats for this date and save them to csv
    track_stats = extract_data(url)
    track_stats.to_csv(save_filename.format(track_type, season, season_type, date), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get tracking stats day-by-day for multiple seasons
def get_tracking_stats_every_day(seasons, season_types, schedule_filename, save_filename, fail_filename):
    failed_dates = {}
    for season in seasons:
        for season_type in season_types:
            # Read schedule
            schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

            # Extract the dates from the schedule
            dates = schedule['GAME_DATE'].unique()
            n_dates = len(dates)
            n_types = len(track_types)

            # Get tracking stats for each day in schedule
            for i, date in enumerate(dates):
                for j, track_type in enumerate(track_types):
                    print(
                        f'{((i * n_types + j) / (n_dates * n_types)):.2%} {season} {season_type}: {date} {track_type}')
                    try:
                        get_tracking_stats_single_day(date, season, season_type, track_type, save_filename)
                    except Exception as error:
                        print(error)
                        traceback.print_exc()
                        failed_dates[date] = str(error), traceback.format_exc()

        # Save failed dates
        with open(fail_filename, 'wb') as fp:
            pickle.dump(failed_dates, fp)


# Get tracking stats for an entire season
def get_tracking_stats_whole_season(season, season_type, track_type, save_filename):
    # Format tracking stats URL to get stats for season
    url = track_url.format(start_date='',
                           end_date='',
                           per_mode='Totals',
                           track_type=track_type,
                           season=season,
                           season_type=season_type)

    # Get the tracking stats for this season and save them to csv
    track_stats = extract_data(url)
    track_stats.to_csv(save_filename.format(track_type, season, season_type), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(0.75)


# Get tracking stats for entire seasons
def get_tracking_stats_seasons(seasons, season_types, save_filename, fail_filename):
    # Keep track of failed seasons
    failed_seasons = {}

    # Constants for finding completion percentage
    n_seasons = len(seasons)
    n_season_types = len(season_types)
    n_track_types = len(track_types)

    # Get tracking stats for each season
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            for k, track_type in enumerate(track_types):
                percent_done = (((i * n_season_types * n_track_types) + (j * n_track_types) + k) /
                                (n_seasons * n_season_types * n_track_types))
                print(f'{percent_done:.2%} {season} {season_type}: {track_type}')

                # Get tracking stats
                try:
                    get_tracking_stats_whole_season(season, season_type, track_type, save_filename)
                except Exception as error:
                    print(error)
                    traceback.print_exc()
                    failed_seasons[f'{season} {season_type} {track_type}'] = str(error), traceback.format_exc()

    # Save failed seasons
    with open(fail_filename, 'wb') as fp:
        pickle.dump(failed_seasons, fp)


if __name__ == '__main__':
    seasons = range(2013, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    whole_season_save_filename = '../Data/SeasonStats/Tracking/{}/{}_{}.csv'
    single_day_save_filename = '../Data/BoxScores/Tracking/{}/{}_{}_{}.csv'
    # get_tracking_stats_every_day(seasons, season_types, schedule_filename, single_day_save_filename, 'Fails/failed_dates.pkl')
    get_tracking_stats_seasons(seasons, season_types, whole_season_save_filename, 'Fails/tracking.pkl')

    # with open('Fails/tracking.pkl', 'rb') as fp:
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


    # if track_type == 'CatchShoot':
    #     print()
    # elif track_type == 'Drives':
    #     print()
    # elif track_type == 'Defense':
    #     print()
    # elif track_type == 'Passing':
    #     print()
    # elif track_type == 'Possessions':  # Touches
    #     print()
    # elif track_type == 'PullUpShot':
    #     print()
    # elif track_type == 'Rebounding':  # Includes base, offense, and defense
    #     print()
    # elif track_type == 'Efficiency':
    #     print()
    # elif track_type == 'SpeedDistance':
    #     print()
    # elif track_type == 'ElbowTouch':
    #     print()
    # elif track_type == 'PostTouch':
    #     print()
    # elif track_type == 'PaintTouch':
    #     print()
