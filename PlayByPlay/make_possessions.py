import pandas as pd
from play_by_play_helpers import *


# Convert string representation of a list to an actual list
def string_to_list(list_str):
    # Remove brackets
    list_str_no_brackets = list_str.replace('[', '').replace(']', '')

    # Convert comma-separated values to list
    return list_str_no_brackets.split(', ')


# Add the players on the court to an event
def add_players_on_court_to_event(event, sub_map):
    # Get the period for the event
    period = event[period_column]

    # If the event is a substitution, sub out the players on the court
    if EventType.from_number(event[event_type]) == EventType.Substitution:
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

    # Add players on court for each team to event
    for i, team_id in enumerate(sub_map[period].keys()):
        event['TEAM{}_ID'.format(i + 1)] = team_id
        event['TEAM{}_PLAYER1'.format(i + 1)] = sub_map[period][team_id][0]
        event['TEAM{}_PLAYER2'.format(i + 1)] = sub_map[period][team_id][1]
        event['TEAM{}_PLAYER3'.format(i + 1)] = sub_map[period][team_id][2]
        event['TEAM{}_PLAYER4'.format(i + 1)] = sub_map[period][team_id][3]
        event['TEAM{}_PLAYER5'.format(i + 1)] = sub_map[period][team_id][4]


# Group events into possessions
def get_possessions(events, sub_map):
    # Store list of possessions and current possession
    possessions = []
    current_possession = []
    for idx, event in events:
        # Add players on the court to the event
        add_players_on_court_to_event(event, sub_map)

        # Get the type of event
        e_type = EventType.from_number(event[event_type])

        # Do not include substitutions or end of periods to events in possession
        if e_type != EventType.Substitution and e_type != EventType.EndOfPeriod:
            current_possession.append(event)

        # If event is end of possession, add the possession to the list of possessions
        if is_end_of_possession(idx, event, events):
            # Do not add empty possessions
            if len(current_possession) > 0:
                possessions.append(current_possession)

            # Reset current possession
            current_possession = []

    return possessions


# Count points for each team in a possession
def count_points_in_possession(possession):
    # Map team IDs to points in the possession
    points = {}

    # Check each event in possession for points
    for event in possession:
        # Get the event type
        e_type = EventType.from_number(event[event_type])

        # Check if event is a made shot or made free throw
        if e_type == EventType.MadeShot or (e_type == EventType.FreeThrow and not is_miss(event)):
            # If the team has already scored points in the possession, add to the total
            if event[player1_team_id] in points:
                points[event[player1_team_id]] += extract_points(event)

            # If the team has not already scored points in the possession, create key-value pair
            else:
                points[event[player1_team_id]] = extract_points(event)

    return points


# Determine which team had possession of the ball based on the last event in the possession
def get_possession_team(event, team1, team2):
    # Get the event type
    e_type = EventType.from_number(event[event_type])

    # If the last event was a made shot or made free throw, return the team that made the shot or free throw
    if e_type == EventType.MadeShot or e_type == EventType.FreeThrow:
        return str(int(event[player1_team_id]))

    # If the last event was a rebound, return the team that did not get the rebound
    elif e_type == EventType.Rebound:
        # Handle team rebounds
        if is_team_rebound(event):
            return team2 if event[player1_id] == team1 else team1

        # Handle individual rebounds
        else:
            return team2 if event[player1_team_id] == team1 else team1

    # If the last event was a turnover, return the team that committed the turnover
    elif e_type == EventType.Turnover:
        # Handle team turnovers
        if is_team_turnover(event):
            return str(int(event[player1_id]))

        # Handle individual turnovers
        else:
            return str(int(event[player1_team_id]))

    # If the last event was none of the above, then it was (likely) the last event before the end of the period,
    # so return whatever team player 1 was on. TODO: Handle event type cases differently to ensure reliability
    else:
        # Handle when the event is a team event
        if math.isnan(event[player1_team_id]):
            return str(int(event[player1_id]))

        # Handle when the event is an individual event
        else:
            return str(int(event[player1_team_id]))


# Create a dictionary for a possession that includes the game id, period, teams, players on the court, start and
# end time of the possession, points scored by each team, and which team was on offense during the possession.
def create_possession_dictionary(possession):
    # Get the start time and end time of possession
    times_of_events = [event[time_elapsed] for event in possession]
    possession_start = min(times_of_events)
    possession_end = max(times_of_events)

    # Get the points scored in the possession
    points = count_points_in_possession(possession)

    # Get the game ID
    game_id = possession[0]['GAME_ID']

    # Get the period
    period = possession[0][period_column]

    # Get the first team ID
    team1_id = possession[0]['TEAM1_ID']

    # Get player IDs for the first team
    team1_player1 = possession[0]['TEAM1_PLAYER1']
    team1_player2 = possession[0]['TEAM1_PLAYER2']
    team1_player3 = possession[0]['TEAM1_PLAYER3']
    team1_player4 = possession[0]['TEAM1_PLAYER4']
    team1_player5 = possession[0]['TEAM1_PLAYER5']

    # Get the points scored for the first team
    team1_points = points[team1_id] if team1_id in points else 0

    # Get second team ID
    team2_id = possession[0]['TEAM2_ID']

    # Get player IDs for the second team
    team2_player1 = possession[0]['TEAM2_PLAYER1']
    team2_player2 = possession[0]['TEAM2_PLAYER2']
    team2_player3 = possession[0]['TEAM2_PLAYER3']
    team2_player4 = possession[0]['TEAM2_PLAYER4']
    team2_player5 = possession[0]['TEAM2_PLAYER5']

    # Get the points scored for the second team
    team2_points = points[team2_id] if team2_id in points else 0

    # Find the team who was on offense for the possession
    possession_team = get_possession_team(possession[-1], team1_id, team2_id)

    return {
        'team1_id': str(team1_id),
        'team1_player1': str(team1_player1),
        'team1_player2': str(team1_player2),
        'team1_player3': str(team1_player3),
        'team1_player4': str(team1_player4),
        'team1_player5': str(team1_player5),
        'team2_id': str(team2_id),
        'team2_player1': str(team2_player1),
        'team2_player2': str(team2_player2),
        'team2_player3': str(team2_player3),
        'team2_player4': str(team2_player4),
        'team2_player5': str(team2_player5),
        'game_id': str(game_id),
        'period': period,
        'possession_start': possession_start,
        'possession_end': possession_end,
        'team1_points': team1_points,
        'team2_points': team2_points,
        'possession_team': str(possession_team)
    }


# Get every possession in a single game
def get_possessions_single_game(game_id, play_by_play_filename, players_at_period_filename, possessions_filename):
    # Read in play-by-play data for the game
    play_by_play = pd.read_csv(play_by_play_filename.format(game_id), index_col=False)

    # Fill NA descriptions with empty strings
    play_by_play[home_description] = play_by_play[home_description].fillna("")
    play_by_play[neutral_description] = play_by_play[home_description].fillna("")
    play_by_play[away_description] = play_by_play[away_description].fillna("")

    # Add columns for the time elapsed in the game and in the period
    play_by_play[time_elapsed] = play_by_play.apply(get_time_elapsed_game, axis=1)
    play_by_play[time_elapsed_period] = play_by_play.apply(get_time_elapsed_period, axis=1)

    # Read the players at the start of each period for the game
    players_at_start_of_period = pd.read_csv(players_at_period_filename.format(game_id))

    # Keep track of the players on the court for each team for each period
    sub_map = {}

    # Pre-populate the map with the players at the start of each period
    for _, period in players_at_start_of_period.iterrows():
        sub_map[period[period_column]] = {period['TEAM_ID_1']: string_to_list(period['TEAM_1_PLAYERS']),
                                          period['TEAM_ID_2']: string_to_list(period['TEAM_2_PLAYERS'])}

    # Convert play-by-play dataframe into a list of events
    pbp_events = list(play_by_play.iterrows())

    # Get possessions for game from list of events
    possessions = get_possessions(pbp_events, sub_map)

    # Get possession dictionary for each possession in game
    possession_dictionaries = []
    for possession in possessions:
        possession_dictionaries.append(create_possession_dictionary(possession))

    # Build a dataframe from the list of possession dictionaries
    possessions_df = pd.DataFrame(possession_dictionaries)

    # Sort the columns alphabetically
    possessions_df = possessions_df.reindex(sorted(possessions_df.columns), axis=1)

    # Save possessions dataframe to a .csv file
    possessions_df.to_csv(possessions_filename.format(game_id), index=False)


if __name__ == '__main__':
    # play_by_play_filename = '../Data/PlayByPlay/pbp_{}.csv'
    # players_at_period_filename = '../Data/PlayersAtPeriod/pap_{}.csv'
    # possessions_filename = '../Data/Possessions/possessions_{}.csv'
    play_by_play_filename = '../../NBA Tutorials/play_by_play_parser/data/0021801167_pbp.csv'
    players_at_period_filename = '../../NBA Tutorials/play_by_play_parser/data/0021801167_players_at_period.csv'
    possessions_filename = 'test.csv'
    get_possessions_single_game('0021801167', play_by_play_filename, players_at_period_filename, possessions_filename)
