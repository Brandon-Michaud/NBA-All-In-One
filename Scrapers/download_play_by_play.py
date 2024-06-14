import time
import pandas as pd
import requests
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
def download_play_by_play(schedule_url, seasons, season_types, schedule_filename, play_by_play_url, play_by_play_filename):
    # Loop over seasons and regular season/playoffs
    for season in seasons:
        for season_type in season_types:
            # Extract schedule data for the season and season type
            url = schedule_url.format(season, season_type)
            schedule = extract_data(url)

            # Save schedule in case it is needed later
            schedule.to_csv(schedule_filename.format(season, season_type), index=False)

            # Extract the game IDs from the schedule
            game_ids = schedule['GAME_ID'].unique()
            n_games = len(game_ids)

            # Scrape the play-by-play for every game
            for i, game_id in enumerate(game_ids):
                print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')
                play_by_play = extract_data(play_by_play_url.format(game_id))

                # Save the play-by-play data
                play_by_play.to_csv(play_by_play_filename.format(game_id), index=False)

                # Sleep for 0.75 seconds to stay under the rate limit
                time.sleep(.75)


if __name__ == '__main__':
    seasons = range(2019, 2023)
    seasons = [f'{season}-{int(str(season)[2:]) + 1}' for season in seasons]
    season_types = ['Regular Season', 'PlayIn', 'Playoffs']
    schedule_url = "http://stats.nba.com/stats/leaguegamelog/?leagueId=00&season={}&seasonType={}&playerOrTeam=T&counter=0&sorter=PTS&direction=ASC&dateFrom=&dateTo="
    play_by_play_url = "https://stats.nba.com/stats/playbyplayv2/?gameId={0}&startPeriod=0&endPeriod=14"
    download_play_by_play(schedule_url, seasons, season_types, '../Data/Schedules/schedule_{}_{}.csv', play_by_play_url, '../Data/PlayByPlay/pbp_{}.csv')
