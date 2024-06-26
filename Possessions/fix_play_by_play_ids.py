import pandas as pd
import math


# Fix player ID errors in 1996-97 play-by-play
# I found two separate errors that occur multiple times
# Melvin Booker is often referenced with player ID 775 in play-by-play and his name is not used for the player name,
# it is only found in the descriptions of the events. Looking at the general stats for the season, Melvin Booker's
# actual player ID is 511.
# A similar situation occurs with Lionel Simmons. He is often reference by player ID 471 but his actual player ID is
# 1489
# This code simply looks for these errors and corrects them
def fix_play_by_play_ids():
    # Read schedule
    schedule = pd.read_csv('../Data/Schedules/schedule_1996-97_Regular Season.csv', dtype=str)

    # Extract the game IDs from the schedule
    game_ids = schedule['GAME_ID'].unique()
    n_games = len(game_ids)

    # Get possessions for each game
    for i, game_id in enumerate(game_ids):
        print(f'{((i + 1) / n_games):.2%}: {game_id}')

        # Load play-by-play data
        play_by_play = pd.read_csv(f'../Data/PlayByPlay/Standard/pbp_{game_id}.csv')

        # Fix player ID errors in play-by-play
        for i, event in play_by_play.iterrows():
            if event['PLAYER1_ID'] == 775 and math.isnan(event['PLAYER1_NAME']):
                play_by_play.loc[i, 'PLAYER1_ID'] = 511
                play_by_play.loc[i, 'PLAYER1_NAME'] = 'Melvin Booker'
            elif event['PLAYER2_ID'] == 775 and math.isnan(event['PLAYER2_NAME']):
                play_by_play.loc[i, 'PLAYER2_ID'] = 511
                play_by_play.loc[i, 'PLAYER2_NAME'] = 'Melvin Booker'
            elif event['PLAYER3_ID'] == 775 and math.isnan(event['PLAYER3_NAME']):
                play_by_play.loc[i, 'PLAYER3_ID'] = 511
                play_by_play.loc[i, 'PLAYER3_NAME'] = 'Melvin Booker'
            elif event['PLAYER1_ID'] == 471 and math.isnan(event['PLAYER1_NAME']):
                play_by_play.loc[i, 'PLAYER1_ID'] = 1489
                play_by_play.loc[i, 'PLAYER1_NAME'] = 'Lionel Simmons'
            elif event['PLAYER2_ID'] == 471 and math.isnan(event['PLAYER2_NAME']):
                play_by_play.loc[i, 'PLAYER2_ID'] = 1489
                play_by_play.loc[i, 'PLAYER2_NAME'] = 'Lionel Simmons'
            elif event['PLAYER3_ID'] == 471 and math.isnan(event['PLAYER3_NAME']):
                play_by_play.loc[i, 'PLAYER3_ID'] = 1489
                play_by_play.loc[i, 'PLAYER3_NAME'] = 'Lionel Simmons'

        # Save fixed play-by-play
        play_by_play.to_csv(f'../Data/PlayByPlay/Standard/pbp_{game_id}.csv')


if __name__ == '__main__':
    fix_play_by_play_ids()