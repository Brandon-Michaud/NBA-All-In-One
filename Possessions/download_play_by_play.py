import pickle
import time
import traceback

from api_helpers import *


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

            # Remove missing/wrong games
            schedule = schedule[schedule['WL'].notna()]

            # Save schedule in case it is needed later
            schedule.to_csv(schedule_filename.format(season, season_type), index=False)

            # Extract the game IDs from the schedule
            game_ids = schedule['GAME_ID'].unique()
            n_games = len(game_ids)

            # Scrape the play-by-play for every game
            for i, game_id in enumerate(game_ids):
                print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')

                # Scrape play-by-play for the game
                results = download_play_by_play_single_game(game_id, play_by_play_url, play_by_play_filename)

                # Check if there was an error
                if results[0] != 0:
                    failures[game_id] = results[1:]

    # Save failed links
    with open(failed_filename, 'wb') as fp:
        pickle.dump(failures, fp)


# Download play-by-play data for a single game
def download_play_by_play_single_game(game_id, play_by_play_url, play_by_play_filename):
    try:
        play_by_play = extract_data(play_by_play_url.format(game_id))
    except Exception as error:
        print(f'Error occurred: {error}')
        traceback.print_exc()
        return -1, str(error), traceback.format_exc()

    # Save the play-by-play data
    play_by_play.to_csv(play_by_play_filename.format(game_id), index=False)

    # Sleep for 0.75 seconds to stay under the rate limit
    time.sleep(.75)

    # Return success code
    return 0,


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_url = "http://stats.nba.com/stats/leaguegamelog/?leagueId=00&season={}&seasonType={}&playerOrTeam=T&counter=0&sorter=PTS&direction=ASC&dateFrom=&dateTo="
    play_by_play_url = "https://stats.nba.com/stats/playbyplayv2/?gameId={0}&startPeriod=0&endPeriod=14"
    download_play_by_play(schedule_url, seasons, season_types, '../Data/Schedules/schedule_{}_{}.csv', play_by_play_url, '../Data/PlayByPlay/Standard/pbp_{}.csv', 'Fails/failed_play_by_plays.pkl')
