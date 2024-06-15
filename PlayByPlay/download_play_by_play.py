import time
import pandas as pd
import requests
import pickle
import traceback
from api_headers import *


# Extract the JSON data from HTTP response from stats.nba.com
def extract_data(url):
    # Send request and get response
    response = requests.get(url, headers=stats_nba_com_headers)
    response = response.json()

    # Get headers and rows from response
    result = response['resultSets'][0]
    headers = result['headers']
    rows = result['rowSet']

    # Convert response to data frame
    result_df = pd.DataFrame(rows)
    result_df.columns = headers

    return result_df


# Download play-by-play data for given seasons
def download_play_by_play(schedule_url, seasons, season_types, schedule_filename, play_by_play_url, play_by_play_filename, failed_filename):
    # Keep track of failed downloads
    failures = {}

    # Loop over seasons and regular season/playoffs
    for season in seasons:
        for season_type in season_types:
            # Extract schedule data for the season and season type
            try:
                schedule = extract_data(schedule_url.format(season, season_type))
            except Exception as error:
                print(f'Error occurred: {error}')
                traceback.print_exc()
                failures[schedule_url.format(season, season_type)] = (error, traceback.format_exc())
                continue

            # Save schedule in case it is needed later
            schedule.to_csv(schedule_filename.format(season, season_type), index=False)

            # Extract the game IDs from the schedule
            game_ids = schedule['GAME_ID'].unique()
            n_games = len(game_ids)

            # Scrape the play-by-play for every game
            for i, game_id in enumerate(game_ids):
                print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')
                try:
                    play_by_play = extract_data(play_by_play_url.format(game_id))
                except Exception as error:
                    print(f'Error occurred: {error}')
                    traceback.print_exc()
                    failures[play_by_play_url.format(game_id)] = (str(error), traceback.format_exc())
                    continue

                # Save the play-by-play data
                play_by_play.to_csv(play_by_play_filename.format(game_id), index=False)

                # Sleep for 0.75 seconds to stay under the rate limit
                time.sleep(.75)

    # Save failed links
    with open(failed_filename, 'wb') as fp:
        pickle.dump(failures, fp)


if __name__ == '__main__':
    seasons = range(2019, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['PlayIn']
    schedule_url = "http://stats.nba.com/stats/leaguegamelog/?leagueId=00&season={}&seasonType={}&playerOrTeam=T&counter=0&sorter=PTS&direction=ASC&dateFrom=&dateTo="
    play_by_play_url = "https://stats.nba.com/stats/playbyplayv2/?gameId={0}&startPeriod=0&endPeriod=14"
    download_play_by_play(schedule_url, seasons, season_types, '../Data/Schedules/schedule_{}_{}.csv', play_by_play_url, '../Data/PlayByPlay/pbp_{}.csv', 'failed_links2.pkl')
