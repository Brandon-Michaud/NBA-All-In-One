from Possessions.play_by_play_helpers import *


# Luck-adjust a play-by-play for a single game
def luck_adjust_play_by_play_single_game(game_id, stats, play_by_play_filename, luck_adjusted_play_by_play_filename):
    # Read in play-by-play data for the game
    play_by_play = pd.read_csv(play_by_play_filename.format(game_id))

    # Fill NA descriptions with empty strings
    play_by_play[home_description] = play_by_play[home_description].fillna("")
    play_by_play[neutral_description] = play_by_play[home_description].fillna("")
    play_by_play[away_description] = play_by_play[away_description].fillna("")

    # Add column for points for each EVENT initialized to 0
    play_by_play['POINTS'] = 0.0

    # Add luck-adjusted points value for every event
    for idx, event in play_by_play.iterrows():
        # Get the event type
        e_type = EventType.from_number(event[event_type])
        player_id = event[player1_id]

        # Adjust point values for threes
        if (e_type == EventType.MadeShot or e_type == EventType.MissedShot) and is_three(event):
            # Set points to average point value for a three from this player
            player_stats = stats[stats['PLAYER_ID'] == player_id].iloc[0]
            three_value = (player_stats['FG3M'] / player_stats['FG3A']) * 3
            play_by_play.at[idx, 'POINTS'] = three_value

        # Adjust point values for free throws
        elif e_type == EventType.FreeThrow:
            # Set points to average point value for a free throw from this player
            player_stats = stats[stats['PLAYER_ID'] == player_id].iloc[0]
            ft_value = player_stats['FTM'] / player_stats['FTA']
            play_by_play.at[idx, 'POINTS'] = ft_value

        # Add point values for twos
        elif e_type == EventType.MadeShot and not is_three(event):
            play_by_play.at[idx, 'POINTS'] = 2

    # Save luck-adjusted play-by-play to csv
    play_by_play.to_csv(luck_adjusted_play_by_play_filename.format(game_id), index=False)


# Luck-adjust play-by-plays for every season
def luck_adjust_play_by_plays(seasons, season_types, schedule_filename, stats_filename, play_by_play_filename,
                              luck_adjusted_play_by_play_filename):
    # Loop over seasons and regular season/playoffs
    for season in seasons:
        for season_type in season_types:
            # Read schedule
            schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

            # Extract the game IDs from the schedule
            game_ids = schedule['GAME_ID'].unique()
            n_games = len(game_ids)

            # Read in player stats for the season
            stats = pd.read_csv(stats_filename.format(season, season_type))

            # Get possessions for each game
            for i, game_id in enumerate(game_ids):
                print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')

                # Luck-adjust play-by-play for this game
                luck_adjust_play_by_play_single_game(game_id, stats, play_by_play_filename,
                                                     luck_adjusted_play_by_play_filename)


if __name__ == '__main__':
    seasons = range(2023, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    play_by_play_filename = '../Data/PlayByPlay/Standard/pbp_{}.csv'
    stats_filename = '../Data/SeasonStats/General/Base/{}_{}.csv'
    luck_adjusted_play_by_play_filename = '../Data/PlayByPlay/LuckAdjusted/pbp_{}.csv'
    luck_adjust_play_by_plays(seasons, season_types, schedule_filename, stats_filename, play_by_play_filename,
                              luck_adjusted_play_by_play_filename)
