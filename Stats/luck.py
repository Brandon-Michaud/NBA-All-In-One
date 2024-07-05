import copy
import pickle

import pandas as pd

from Possessions.play_by_play_helpers import *
from Possessions.make_possessions import string_to_list

# Initial data structure for storing shooting splits for a player based on which teammates and opponents are on floor
initial_shooting_splits_with_players_on_court = {
    'TEAMMATES': {},
    'OPPONENTS': {},
    'TOTAL': {
        'FG3A': 0,
        'FG3M': 0,
        'FTA': 0,
        'FTM': 0,
    },
}

# Initial shooting splits
initial_shooting_splits = {
    'FG3A': 0,
    'FG3M': 0,
    'FTA': 0,
    'FTM': 0,
}

# Initial luck adjustments
initial_luck_splits = {
    'ACTUAL': {
        'TEAMMATES': {
            'FG3A': 0,
            'FG3M': 0,
            'FTA': 0,
            'FTM': 0,
        },
        'OPPONENTS': {
            'FG3A': 0,
            'FG3M': 0,
            'FTA': 0,
            'FTM': 0,
        },
    },
    'LUCK_ADJUSTED': {
        'TEAMMATES': {
            'FG3A': 0,
            'FG3M': 0,
            'FTA': 0,
            'FTM': 0,
        },
        'OPPONENTS': {
            'FG3A': 0,
            'FG3M': 0,
            'FTA': 0,
            'FTM': 0,
        },
    },
}


# Get shooting splits for each player, split based on who was on the court for the shot
# First key is shooter ID, second key is ID for players who were on the court for the shot
def get_shooting_splits_with_players_on_court_single_season(season, season_type, schedule_filename,
                                                            play_by_play_filename, period_starters_filename,
                                                            teammates_and_opponents_filename):
    # Get the schedule for the season
    schedule = pd.read_csv(schedule_filename.format(season, season_type), dtype=str)

    # Get all the games for the season
    game_ids = schedule['GAME_ID'].unique()
    n_games = len(game_ids)

    # Keep track of teammates and opponents
    all_players_teammates_opponents = {}

    # Get the teammates and opponents for each player for each game
    for i, game_id in enumerate(game_ids):
        print(f'{((i + 1) / n_games):.2%} {season} {season_type}: {game_id}')

        # Get the play-by-play for the game
        play_by_play = pd.read_csv(play_by_play_filename.format(game_id))

        # Get the starters for each period of the game
        period_starters = pd.read_csv(period_starters_filename.format(game_id))

        # Fill NA descriptions with empty strings
        play_by_play[home_description] = play_by_play[home_description].fillna("")
        play_by_play[neutral_description] = play_by_play[home_description].fillna("")
        play_by_play[away_description] = play_by_play[away_description].fillna("")

        # Keep track of the players on the court for each team for each period
        sub_map = {}

        # Pre-populate the map with the players at the start of each period
        for _, period in period_starters.iterrows():
            sub_map[period[period_column]] = {period['TEAM_ID_1']: string_to_list(period['TEAM_1_PLAYERS']),
                                              period['TEAM_ID_2']: string_to_list(period['TEAM_2_PLAYERS'])}

        # Get team IDs for both teams
        team_ids = [period_starters.iloc[0]['TEAM_ID_1'], period_starters.iloc[0]['TEAM_ID_2']]

        # Loop over each event in the play-by-play
        for _, event in play_by_play.iterrows():
            # Get the period for the event
            period = event[period_column]

            # Get the type of event
            e_type = EventType.from_number(event[event_type])

            # If the event is a substitution, sub out the players on the court
            if e_type == EventType.Substitution:
                # Get the team who is substituting
                team_id = event[player1_team_id]

                # Get substitution players
                player_in = str(event[player2_id])
                player_out = str(event[player1_id])

                # Get players on court before substitution
                players = sub_map[period][team_id]

                # Replace player being subbed out with player being subbed in
                players[players.index(player_out)] = player_in

                # Sort the new list of players
                players.sort()

                # Update the players on the court
                sub_map[period][team_id] = players

            # If the event is a three-point shot attempt or a free throw attempt
            elif is_three(event) or e_type == EventType.FreeThrow:
                # Get the shooter, team of the shooter, and opposing team
                shooter_id = event[player1_id]
                shooter_team_id = int(event[player1_team_id])
                if shooter_team_id == team_ids[0]:
                    opponent_team_id = team_ids[1]
                else:
                    opponent_team_id = team_ids[0]

                # Initialize shooter teammates and opponents if not done so already
                if shooter_id not in all_players_teammates_opponents:
                    all_players_teammates_opponents[shooter_id] = (
                        copy.deepcopy(initial_shooting_splits_with_players_on_court))

                # Add shot to totals for the player
                all_players_teammates_opponents[shooter_id]['TOTAL']['FG3A' if is_three(event) else 'FTA'] += 1
                if e_type == EventType.MadeShot or not is_miss(event):
                    all_players_teammates_opponents[shooter_id]['TOTAL']['FG3M' if is_three(event) else 'FTM'] += 1

                # Add teammates on the court for the shot
                for teammate_id in sub_map[period][shooter_team_id]:
                    # Do not add shooter to own list of teammates
                    if teammate_id == str(shooter_id):
                        continue

                    # Initialize the shooting splits if they have not been
                    if teammate_id not in all_players_teammates_opponents[shooter_id]['TEAMMATES']:
                        all_players_teammates_opponents[shooter_id]['TEAMMATES'][teammate_id] = (
                            copy.deepcopy(initial_shooting_splits))

                    # Add shot for the teammate
                    all_players_teammates_opponents[shooter_id]['TEAMMATES'][teammate_id]['FG3A' if is_three(event) else 'FTA'] += 1
                    if e_type == EventType.MadeShot or not is_miss(event):
                        all_players_teammates_opponents[shooter_id]['TEAMMATES'][teammate_id]['FG3M' if is_three(event) else 'FTM'] += 1

                # Add opponents on the court for the shot
                for opponent_id in sub_map[period][opponent_team_id]:
                    # Initialize the shooting splits if they have not been
                    if opponent_id not in all_players_teammates_opponents[shooter_id]['OPPONENTS']:
                        all_players_teammates_opponents[shooter_id]['OPPONENTS'][opponent_id] = (
                            copy.deepcopy(initial_shooting_splits))

                    # Add shot for the opponent
                    all_players_teammates_opponents[shooter_id]['OPPONENTS'][opponent_id]['FG3A' if is_three(event) else 'FTA'] += 1
                    if e_type == EventType.MadeShot or not is_miss(event):
                        all_players_teammates_opponents[shooter_id]['OPPONENTS'][opponent_id]['FG3M' if is_three(event) else 'FTM'] += 1

    # Save the teammates and opponents to a pickle file
    with open(teammates_and_opponents_filename.format(season, season_type), 'wb') as fp:
        pickle.dump(all_players_teammates_opponents, fp)


# Get all teammates and opponents for each player season-by-season
def get_shooting_splits_with_players_on_court_seasons(seasons, season_types, schedule_filename, play_by_play_filename,
                                                      period_starters_filename, teammates_and_opponents_filename):
    # Loop over every season
    for season in seasons:
        for season_type in season_types:
            # Get all teammates and opponents for each player for a single season
            get_shooting_splits_with_players_on_court_single_season(season, season_type, schedule_filename,
                                                                    play_by_play_filename, period_starters_filename,
                                                                    teammates_and_opponents_filename)


# Get luck splits for each player in a single season
# First key is the player ID, the second key is the player ID of any teammate or opponent who took a shot while the
# player was on the court
def get_luck_splits_single_season(season, season_type, teammates_and_opponents_filename, luck_splits_filename):
    # Load teammates and opponents data
    with open(teammates_and_opponents_filename.format(season, season_type), 'rb') as fp:
        teammates_and_opponents = pickle.load(fp)

    # Keep track of shooting splits of teammates and opponents for every player
    all_player_luck_splits = {}

    # Find luck adjustments for each player
    for shooter_id in teammates_and_opponents:
        # Get the shooting percentages for the shooter for the entire season
        shooter_fg3_percentage = 0
        shooter_ft_percentage = 0
        if teammates_and_opponents[shooter_id]['TOTAL']['FG3A'] != 0:
            shooter_fg3_percentage = teammates_and_opponents[shooter_id]['TOTAL']['FG3M'] / teammates_and_opponents[shooter_id]['TOTAL']['FG3A']
        if teammates_and_opponents[shooter_id]['TOTAL']['FTA'] != 0:
            shooter_ft_percentage = teammates_and_opponents[shooter_id]['TOTAL']['FTM'] / teammates_and_opponents[shooter_id]['TOTAL']['FTA']

        # Add to running luck adjustments for each teammate
        for teammate_id in teammates_and_opponents[shooter_id]['TEAMMATES']:
            # Initialize running luck adjustment for teammate if not done so already
            if teammate_id not in all_player_luck_splits:
                all_player_luck_splits[teammate_id] = copy.deepcopy(initial_luck_splits)

            # Reverse totals so that primary key is teammate of shooter instead of shooter and add splits to running
            # totals
            for stat in teammates_and_opponents[shooter_id]['TEAMMATES'][teammate_id]:
                all_player_luck_splits[teammate_id]['ACTUAL']['TEAMMATES'][stat] += (
                    teammates_and_opponents)[shooter_id]['TEAMMATES'][teammate_id][stat]

            # Add luck-adjusted shooting splits to running totals
            all_player_luck_splits[teammate_id]['LUCK_ADJUSTED']['TEAMMATES']['FG3M'] += (
                    shooter_fg3_percentage * teammates_and_opponents[shooter_id]['TEAMMATES'][teammate_id]['FG3A'])
            all_player_luck_splits[teammate_id]['LUCK_ADJUSTED']['TEAMMATES']['FG3A'] += (
                    teammates_and_opponents[shooter_id]['TEAMMATES'][teammate_id]['FG3A'])
            all_player_luck_splits[teammate_id]['LUCK_ADJUSTED']['TEAMMATES']['FTM'] += (
                    shooter_ft_percentage * teammates_and_opponents[shooter_id]['TEAMMATES'][teammate_id]['FTA'])
            all_player_luck_splits[teammate_id]['LUCK_ADJUSTED']['TEAMMATES']['FTA'] += (
                    teammates_and_opponents[shooter_id]['TEAMMATES'][teammate_id]['FTA'])

        # Add to running luck adjustments for each opponent
        for opponent_id in teammates_and_opponents[shooter_id]['OPPONENTS']:
            # Initialize running luck adjustment for teammate if not done so already
            if opponent_id not in all_player_luck_splits:
                all_player_luck_splits[opponent_id] = copy.deepcopy(initial_luck_splits)

            # Reverse totals so that primary key is teammate of shooter instead of shooter and add splits to running
            # totals
            for stat in teammates_and_opponents[shooter_id]['OPPONENTS'][opponent_id]:
                all_player_luck_splits[opponent_id]['ACTUAL']['OPPONENTS'][stat] += (
                    teammates_and_opponents)[shooter_id]['OPPONENTS'][opponent_id][stat]

            # Add luck-adjusted shooting splits to running totals
            all_player_luck_splits[opponent_id]['LUCK_ADJUSTED']['OPPONENTS']['FG3M'] += (
                    shooter_fg3_percentage * teammates_and_opponents[shooter_id]['OPPONENTS'][opponent_id]['FG3A'])
            all_player_luck_splits[opponent_id]['LUCK_ADJUSTED']['OPPONENTS']['FG3A'] += (
                teammates_and_opponents[shooter_id]['OPPONENTS'][opponent_id]['FG3A'])
            all_player_luck_splits[opponent_id]['LUCK_ADJUSTED']['OPPONENTS']['FTM'] += (
                    shooter_ft_percentage * teammates_and_opponents[shooter_id]['OPPONENTS'][opponent_id]['FTA'])
            all_player_luck_splits[opponent_id]['LUCK_ADJUSTED']['OPPONENTS']['FTA'] += (
                teammates_and_opponents[shooter_id]['OPPONENTS'][opponent_id]['FTA'])

    # Save luck splits to pickle file
    with open(luck_splits_filename.format(season, season_type), 'wb') as fp:
        pickle.dump(all_player_luck_splits, fp)


# Get all luck splits for each player season-by-season
def get_luck_splits_seasons(seasons, season_types, teammates_and_opponents_filename, luck_splits_filename):
    # Loop over every season
    for season in seasons:
        for season_type in season_types:
            # Get luck splits for each player for a single season
            get_luck_splits_single_season(season, season_type, teammates_and_opponents_filename, luck_splits_filename)


# Get luck adjustments for each player in a single season
def get_luck_adjustments_single_season(season, season_type, luck_splits_filename, possessions_filename,
                                       luck_adjustments_filename):
    # Load luck splits data
    with open(luck_splits_filename.format(season, season_type), 'rb') as fp:
        luck_splits = pickle.load(fp)

    # Store luck adjustments for each player
    rows = []

    # Find luck adjustments for each player
    for player_id in luck_splits:
        # Get actual percentages
        actual_teammate_fg3_percentage = 0
        if luck_splits[player_id]['ACTUAL']['TEAMMATES']['FG3A'] != 0:
            actual_teammate_fg3_percentage = (luck_splits[player_id]['ACTUAL']['TEAMMATES']['FG3M'] / 
                                              luck_splits[player_id]['ACTUAL']['TEAMMATES']['FG3A'])
        actual_teammate_ft_percentage = 0
        if luck_splits[player_id]['ACTUAL']['TEAMMATES']['FTA'] != 0:
            actual_teammate_ft_percentage = (luck_splits[player_id]['ACTUAL']['TEAMMATES']['FTM'] / 
                                             luck_splits[player_id]['ACTUAL']['TEAMMATES']['FTA'])
        actual_opponent_fg3_percentage = 0
        if luck_splits[player_id]['ACTUAL']['OPPONENTS']['FG3A'] != 0:
            actual_opponent_fg3_percentage = (luck_splits[player_id]['ACTUAL']['OPPONENTS']['FG3M'] / 
                                              luck_splits[player_id]['ACTUAL']['OPPONENTS']['FG3A'])
        actual_opponent_ft_percentage = 0
        if luck_splits[player_id]['ACTUAL']['OPPONENTS']['FTA'] != 0:
            actual_opponent_ft_percentage = (luck_splits[player_id]['ACTUAL']['OPPONENTS']['FTM'] / 
                                             luck_splits[player_id]['ACTUAL']['OPPONENTS']['FTA'])

        # Get luck-adjusted percentages
        luck_adjusted_teammate_fg3_percentage = 0
        if luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FG3A'] != 0:
            luck_adjusted_teammate_fg3_percentage = (luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FG3M'] / 
                                                     luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FG3A'])
        luck_adjusted_teammate_ft_percentage = 0
        if luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FTA'] != 0:
            luck_adjusted_teammate_ft_percentage = (luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FTM'] / 
                                                    luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FTA'])
        luck_adjusted_opponent_fg3_percentage = 0
        if luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FG3A'] != 0:
            luck_adjusted_opponent_fg3_percentage = (luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FG3M'] / 
                                                     luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FG3A'])
        luck_adjusted_opponent_ft_percentage = 0
        if luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FTA'] != 0:
            luck_adjusted_opponent_ft_percentage = (luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FTM'] / 
                                                    luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FTA'])
            
        # Get actual points from shots
        actual_teammate_fg3_points = (
                3 * actual_teammate_fg3_percentage * luck_splits[player_id]['ACTUAL']['TEAMMATES']['FG3A'])
        actual_teammate_ft_points = (
                actual_teammate_ft_percentage * luck_splits[player_id]['ACTUAL']['TEAMMATES']['FTA'])
        actual_opponent_fg3_points = (
                3 * actual_opponent_fg3_percentage * luck_splits[player_id]['ACTUAL']['OPPONENTS']['FG3A'])
        actual_opponent_ft_points = (
                actual_opponent_ft_percentage * luck_splits[player_id]['ACTUAL']['OPPONENTS']['FTA'])

        # Get luck-adjusted points from shots
        luck_adjusted_teammate_fg3_points = (
                3 * luck_adjusted_teammate_fg3_percentage * luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FG3A'])
        luck_adjusted_teammate_ft_points = (
                luck_adjusted_teammate_ft_percentage * luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FTA'])
        luck_adjusted_opponent_fg3_points = (
                3 * luck_adjusted_opponent_fg3_percentage * luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FG3A'])
        luck_adjusted_opponent_ft_points = (
                luck_adjusted_opponent_ft_percentage * luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FTA'])

        # Get possession counts for player
        possessions = pd.read_csv(possessions_filename.format(season, season_type))
        player_possessions = possessions[possessions['PLAYER_ID'] == int(player_id)].iloc[0]

        # Get luck adjustments
        offensive_luck_adjustment = (luck_adjusted_teammate_fg3_points + luck_adjusted_teammate_ft_points -
                                     actual_teammate_fg3_points - actual_teammate_ft_points)
        defensive_luck_adjustment = (-luck_adjusted_opponent_fg3_points - luck_adjusted_opponent_ft_points +
                                     actual_opponent_fg3_points + actual_opponent_ft_points)

        # Get luck adjustments per possession
        if player_possessions['O_POSS'] != 0:
            offensive_luck_adjustment = offensive_luck_adjustment * 100 / player_possessions['O_POSS']
        if player_possessions['D_POSS'] != 0:
            defensive_luck_adjustment = defensive_luck_adjustment * 100 / player_possessions['D_POSS']
        total_luck_adjustment = offensive_luck_adjustment + defensive_luck_adjustment

        # Add luck adjustments to list for all players
        row = [player_id,
               offensive_luck_adjustment,
               defensive_luck_adjustment,
               total_luck_adjustment,
               luck_splits[player_id]['ACTUAL']['TEAMMATES']['FG3M'], 
               luck_splits[player_id]['ACTUAL']['TEAMMATES']['FG3A'], 
               actual_teammate_fg3_percentage,
               actual_teammate_fg3_points,
               luck_splits[player_id]['ACTUAL']['TEAMMATES']['FTM'], 
               luck_splits[player_id]['ACTUAL']['TEAMMATES']['FTA'], 
               actual_teammate_ft_percentage,
               actual_teammate_ft_points,
               luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FG3M'],
               luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FG3A'],
               luck_adjusted_teammate_fg3_percentage,
               luck_adjusted_teammate_fg3_points,
               luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FTM'],
               luck_splits[player_id]['LUCK_ADJUSTED']['TEAMMATES']['FTA'],
               luck_adjusted_teammate_ft_percentage,
               luck_adjusted_teammate_ft_points,
               luck_splits[player_id]['ACTUAL']['OPPONENTS']['FG3M'],
               luck_splits[player_id]['ACTUAL']['OPPONENTS']['FG3A'],
               actual_opponent_fg3_percentage,
               actual_opponent_fg3_points,
               luck_splits[player_id]['ACTUAL']['OPPONENTS']['FTM'],
               luck_splits[player_id]['ACTUAL']['OPPONENTS']['FTA'],
               actual_opponent_ft_percentage,
               actual_opponent_ft_points,
               luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FG3M'],
               luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FG3A'],
               luck_adjusted_opponent_fg3_percentage,
               luck_adjusted_opponent_fg3_points,
               luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FTM'],
               luck_splits[player_id]['LUCK_ADJUSTED']['OPPONENTS']['FTA'],
               luck_adjusted_opponent_ft_percentage,
               luck_adjusted_opponent_ft_points,
               player_possessions['O_POSS'],
               player_possessions['D_POSS']]
        rows.append(row)

    # Convert luck adjustments to a dataframe
    luck_adjustments_df = pd.DataFrame(rows)
    luck_adjustments_df.columns = ['PLAYER_ID',
                                   'O_LA', 'D_LA', 'LA',
                                   'TEAMMATE_FG3M', 'TEAMMATE_FG3A', 'TEAMMATE_FG3_PERCENTAGE', 'TEAMMATE_FG3_POINTS',
                                   'TEAMMATE_FTM', 'TEAMMATE_FTA', 'TEAMMATE_FT_PERCENTAGE', 'TEAMMATE_FT_POINTS',
                                   'TEAMMATE_LA_FG3M', 'TEAMMATE_LA_FG3A', 'TEAMMATE_LA_FG3_PERCENTAGE', 'TEAMMATE_LA_FG3_POINTS',
                                   'TEAMMATE_LA_FTM', 'TEAMMATE_LA_FTA', 'TEAMMATE_LA_FT_PERCENTAGE', 'TEAMMATE_LA_FT_POINTS',
                                   'OPPONENT_FG3M', 'OPPONENT_FG3A', 'OPPONENT_FG3_PERCENTAGE', 'OPPONENT_FG3_POINTS',
                                   'OPPONENT_FTM', 'OPPONENT_FTA', 'OPPONENT_FT_PERCENTAGE', 'OPPONENT_FT_POINTS',
                                   'OPPONENT_LA_FG3M', 'OPPONENT_LA_FG3A', 'OPPONENT_LA_FG3_PERCENTAGE', 'OPPONENT_LA_FG3_POINTS',
                                   'OPPONENT_LA_FTM', 'OPPONENT_LA_FTA', 'OPPONENT_LA_FT_PERCENTAGE', 'OPPONENT_LA_FT_POINTS',
                                   'O_POSS', 'D_POSS']

    # Save luck adjustments to csv
    luck_adjustments_df.to_csv(luck_adjustments_filename.format(season, season_type), index=False)


# Get luck adjustments for each player season-by-season for multiple seasons
def get_luck_adjustments_seasons(seasons, season_types, luck_splits_filename, luck_adjustments_filename):
    # Loop over every season
    for season in seasons:
        for season_type in season_types:
            # Get luck adjustments for each player for a single season
            get_luck_adjustments_single_season(season, season_type, luck_splits_filename, luck_adjustments_filename)


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    schedule_filename = '../Data/Schedules/schedule_{}_{}.csv'
    play_by_play_filename = '../Data/PlayByPlay/Standard/pbp_{}.csv'
    period_starters_filename = '../Data/PeriodStarters/pap_{}.csv'
    teammates_and_opponents_filename = '../Data/SeasonStats/Luck/TeammatesOpponents/{}_{}.pkl'
    luck_splits_filename = '../Data/SeasonStats/Luck/LuckSplits/{}_{}.pkl'
    possessions_filename = '../Data/SeasonStats/Possessions/{}_{}.csv'
    luck_adjustments_filename = '../Data/SeasonStats/Luck/LuckAdjustments/{}_{}.csv'
    # get_shooting_splits_with_players_on_court_seasons(seasons, season_types, schedule_filename, play_by_play_filename,
    #                                                   period_starters_filename, teammates_and_opponents_filename)
    # get_luck_splits_seasons(seasons, season_types, teammates_and_opponents_filename, luck_splits_filename)
    get_luck_adjustments_single_season('2023-24', 'Regular Season', luck_splits_filename, possessions_filename,
                                       luck_adjustments_filename)
