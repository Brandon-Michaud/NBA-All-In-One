import math
from enum import Enum

import pandas as pd


# Enumeration for type of play-by-play event
class EventType(Enum):
    MadeShot = 1
    MissedShot = 2
    FreeThrow = 3
    Rebound = 4
    Turnover = 5
    Foul = 6
    Violation = 7
    Substitution = 8
    Timeout = 9
    JumpBall = 10
    Ejection = 11
    StartOfPeriod = 12
    EndOfPeriod = 13
    CatchAll = 14
    Unimportant = -1

    @classmethod
    def from_number(cls, number):
        for member in cls:
            if member.value == number:
                return member
        return cls.Unimportant


# Enumeration for type of foul
class FoulType(Enum):
    Personal = 1
    Shooting = 2
    LooseBall = 3
    Offensive = 4
    Inbound = 5
    AwayFromPlay = 6
    Punch = 8
    ClearPath = 9
    DoubleFoul = 10
    Technical = 11
    NonUnsportsmanlike = 12
    Hanging = 13
    Flagrant1 = 14
    Flagrant2 = 15
    DoubleTechnical = 16
    Defensive3Seconds = 17
    DelayOfGame = 18
    Taunting = 19
    ExcessTimeout = 25
    Charge = 26
    PersonalBlock = 27
    PersonalTake = 28
    ShootingBlock = 29
    TooManyPlayers = 30
    Unimportant = -1

    @classmethod
    def from_number(cls, number):
        for member in cls:
            if member.value == number:
                return member
        return cls.Unimportant


# Enumeration for type of rebound
class ReboundType(Enum):
    Player = 0
    Team = 1
    Unimportant = -1

    @classmethod
    def from_number(cls, number):
        for member in cls:
            if member.value == number:
                return member
        return cls.Unimportant


# Enumeration for free throw types
class FreeThrowType(Enum):
    OneOfOne = 10
    OneOfTwo = 11
    TwoOfTwo = 12
    OneOfThree = 13
    TwoOfThree = 14
    ThreeOfThree = 15
    Technical = 16
    Unimportant = -1

    def is_final_multi_ft(self):
        return self == FreeThrowType.TwoOfTwo or self == FreeThrowType.ThreeOfThree

    def is_final_ft(self):
        return self.is_final_multi_ft() or self == FreeThrowType.OneOfOne

    @classmethod
    def from_number(cls, number):
        for member in cls:
            if member.value == number:
                return member
        return cls.Unimportant


# Enumeration for type turnover
class TurnoverType(Enum):
    FiveSecond = 9
    EightSecond = 10
    ShotClock = 11
    TooManyPlayers = 44
    Unimportant = -1

    @classmethod
    def from_number(cls, number):
        for member in cls:
            if member.value == number:
                return member
        return cls.Unimportant


# Constants for column names
event_type = 'EVENTMSGTYPE'
event_subtype = 'EVENTMSGACTIONTYPE'
home_description = 'HOMEDESCRIPTION'
neutral_description = 'NEUTRALDESCRIPTION'
away_description = 'VISITORDESCRIPTION'
period_column = 'PERIOD'
game_clock = 'PCTIMESTRING'
time_elapsed = 'TIME_ELAPSED'
time_elapsed_period = 'TIME_ELAPSED_PERIOD'
player1_id = 'PLAYER1_ID'
player1_team_id = 'PLAYER1_TEAM_ID'
player2_id = 'PLAYER2_ID'


# Check if a free throw (or any event) is a miss
def is_miss(event):
    miss = False
    if event[home_description]:
        miss = miss or 'miss' in event[home_description].lower()
    if event[away_description]:
        miss = miss or 'miss' in event[away_description].lower()
    return miss


# Check if an event is a team rebound
def is_team_rebound(event):
    # Ensure the event is a rebound
    if EventType.from_number(event[event_type]) != EventType.Rebound:
        return False

    # Check if rebound is a team rebound
    return ReboundType.from_number(event[event_subtype]) == ReboundType.Team or math.isnan(event[player1_team_id])


# Check if an event is a defensive rebound
def is_defensive_rebound(idx, event, events, window=10):
    # Ensure event is a rebound
    if EventType.from_number(event[event_type]) != EventType.Rebound:
        return False

    # Get the missed shot leading to rebound
    shot = extract_missed_shot_for_rebound(idx, events, window=window)

    # Check if the team that missed the shot rebounded it
    if is_team_rebound(event):
        return shot[player1_team_id] != event[player1_id]
    else:
        return shot[player1_team_id] != event[player1_team_id]


# Get the missed shot before a rebound
def extract_missed_shot_for_rebound(idx, events, window=10):
    # Look at the previous events in the window
    window_of_events = events[max(0, idx - window): idx]

    # Look at the most recent events first
    window_of_events.reverse()

    # Check every event to see if it is a miss
    for event in window_of_events:
        # Return event if it is a miss
        if is_miss(event[1]) or is_missed_free_throw(event[1]):
            return event[1]

    # Return furthest back event if no miss was found
    return window_of_events[-1][1]


# Check if event is a missed free throw
def is_missed_free_throw(event):
    # Ensure event is a free throw
    if EventType.from_number(event[event_type]) != EventType.FreeThrow:
        return False

    # Check if free throw was missed
    return is_miss(event)


# Check if event is a made final free throw
def is_last_free_throw_made(idx, event, events, window=20):
    # Check event is a free throw
    if EventType.from_number(event[event_type]) != EventType.FreeThrow:
        return False

    # Make sure the free throw was made
    if is_miss(event):
        return False

    # Get the foul before the free throw
    foul = extract_foul_for_last_free_throw(idx, events, window=window)

    # Get the type of free throw and foul
    ft_type = FreeThrowType.from_number(event[event_subtype])
    foul_type = FoulType.from_number(foul[event_subtype])

    # Check if the free throw was the last of multiple
    if ft_type.is_final_multi_ft():
        return True

    # Check to see if possession changes after free throw
    return (ft_type == FreeThrowType.OneOfOne and
            foul_type != FoulType.AwayFromPlay and
            foul_type != FoulType.LooseBall and
            foul_type != FoulType.Inbound)


# Get the foul that led to free throws
def extract_foul_for_last_free_throw(idx, events, window=20):
    # Look at the previous events in the window
    subset_of_events = events[max(0, idx - window): idx]

    # Look at most recent events first
    subset_of_events.reverse()

    # Check each event to see if it was a foul
    for event in subset_of_events:
        # Return event if it was a foul
        if EventType.from_number(event[1][event_type]) == EventType.Foul:
            return event[1]

    # Return furthest back event if no foul was found
    return subset_of_events[0][1]


# Check if an event is an And-1
def is_and_1(idx, event, events, event_window=20, time_window=10):
    # Ensure event is a made shot
    if EventType.from_number(event[event_type]) != EventType.MadeShot:
        return False

    # Look at future events in the window
    subset_of_events = events[idx + 1: min(idx + event_window + 1, len(events))]

    # Check for a foul and then a 1 of 1 free throw
    foul = False
    ft = False
    for sub_ind, e in subset_of_events:
        # Make sure event occurred within time window
        if not event[time_elapsed] <= e[time_elapsed] <= event[time_elapsed] + time_window:
            continue

        # Get the event type
        e_type = EventType.from_number(e[event_type])

        # Check if event is a foul
        if e_type == EventType.Foul:
            # Get type of foul
            foul_type = FoulType.from_number(e[event_subtype])

            # Check if the foul is not a special foul and the shooter received it
            if (foul_type != FoulType.Technical and foul_type != FoulType.LooseBall and
                    foul_type != FoulType.Inbound and e[player2_id] == event[player1_id]):
                foul = True

        # Check if event is a free throw
        elif e_type == EventType.FreeThrow:
            # Get type of free throw
            ft_type = FreeThrowType.from_number(e[event_subtype])

            # Check if the free throw was a 1-of-1 and the shooter shot it
            if ft_type == FreeThrowType.OneOfOne and e[player1_id] == event[player1_id]:
                ft = True

    return foul and ft


# Check if an event is a made shot but not an And-1
def is_make_and_not_and_1(idx, event, events, event_window=20, time_window=10):
    # Ensure event is a made shot
    if EventType.from_number(event[event_type]) != EventType.MadeShot:
        return False

    # Ensure there was not an And-1
    return not is_and_1(idx, event, events, event_window=event_window, time_window=time_window)


# Check if an event is a three pointer
def is_three(event):
    three = False
    if event[home_description]:
        three = three or '3PT' in event[home_description]
    if event[away_description]:
        three = three or '3PT' in event[away_description]
    return three


# Check if an event is a team turnover
def is_team_turnover(event):
    # Ensure event is a turnover
    if EventType.from_number(event[event_type]) != EventType.Turnover:
        return False

    # If no player is listed, assume it is a team turnover
    if no_player_listed(event):
        return True

    # Get type of turnover
    to_type = TurnoverType.from_number(event[event_subtype])

    # Check if event is team turnover
    return (to_type == TurnoverType.FiveSecond or to_type == TurnoverType.EightSecond or
            to_type == TurnoverType.ShotClock or to_type == TurnoverType.TooManyPlayers)


# Check if no player is listed for an event
def no_player_listed(event):
    return math.isnan(event[player1_team_id])


# Check if an event is the end of a possession
def is_end_of_possession(idx, event, events, event_window=20, time_window=10):
    e_type = EventType.from_number(event[event_type])
    return (e_type == EventType.Turnover or is_last_free_throw_made(idx, event, events, window=event_window) or
            is_defensive_rebound(idx, event, events, window=event_window) or
            is_make_and_not_and_1(idx, event, events, event_window=event_window, time_window=time_window) or
            e_type == EventType.EndOfPeriod)


# We need to know how many points each shot is worth:
def extract_points(event, use_points_column=True):
    # If there is a points column, return its value
    if use_points_column and 'POINTS' in event.index:
        return event['POINTS']

    # Get the event type
    e_type = EventType.from_number(event[event_type])

    # 1 point if made free throw
    if e_type == EventType.FreeThrow and not is_miss(event):
        return 1

    # 3 points if made three pointer
    elif e_type == EventType.MadeShot and is_three(event):
        return 3

    # 2 points if made two pointer
    elif e_type == EventType.MadeShot and not is_three(event):
        return 2

    # 0 points for any other event
    else:
        return 0


# Find the time elapsed in a period at a given event
def get_time_elapsed_period(event):
    # Get the time on the clock and the period of the event
    time_str = event[game_clock]
    period = event[period_column]

    # Maximum minutes in a period is 12 unless overtime
    max_minutes = 12 if period < 5 else 5

    # Get minutes and seconds from time string
    [minutes, sec] = time_str.split(':')

    # Convert minutes and seconds to integers
    minutes = int(minutes)
    sec = int(sec)

    # Calculate minutes and seconds elapsed in period
    min_elapsed = max_minutes - minutes - 1
    sec_elapsed = 60 - sec

    # Return time elapsed in period in seconds
    return (min_elapsed * 60) + sec_elapsed


# Find time elapsed in a game at a given event
def get_time_elapsed_game(event):
    # Find time elapsed in current period of game
    time_in_period = get_time_elapsed_period(event)
    period = event[period_column]

    # Calculate total time elapsed up to the start of the current period
    if period > 4:
        return (12 * 60 * 4) + ((period - 5) * 5 * 60) + time_in_period
    else:
        return ((period - 1) * 12 * 60) + time_in_period


if __name__ == '__main__':
    test_pbp = pd.read_csv('../../NBA Tutorials/play_by_play_parser/data/0021801167_pbp.csv')
    test_pbp[time_elapsed] = test_pbp.apply(get_time_elapsed_game, axis=1)
    test_pbp[time_elapsed_period] = test_pbp.apply(get_time_elapsed_period, axis=1)
    events = list(test_pbp.iterrows())
    print(is_and_1(83, events[83][1], events))
