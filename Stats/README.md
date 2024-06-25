# Stats
This directory handles downloading various kinds of player stats from stats.nba.com to use for later applications.
Each file represents a different kind of data that is being downloaded.
All downloaded stats are totals so that no precision is lost from decimal rounding.
Each stat (except play type) has an option to scrape seasons at a time or single days at a time (play type only has seasons).

## Types of Stats
### General
These stats are all either box scores or derived from box scores. 
Availability for these stats begins in 1996-97.
The code is in [`general.py`](general.py)

### Shooting
These stats are all shooting splits based on distance
Availability for these stats begins in 1996-97.
The code is in [`shooting.py`](shooting.py)

### Defense
These stats are all defended shot percentages grouped by distance. 
Availability for these stats begins in 2013-14.
Some players can have multiple rows if they changed teams mid-season, so extra code is needed to combine them.
The code is in [`defense.py`](defense.py)

### Tracking
These stats are all location-based stats.
Availability for these stats begins in 2013-14.
The code is in [`tracking.py`](tracking.py)

### Hustle
These stats are all random things not captured by box scores.
Availability differs depending on the stat.
Shot contests, charges, screens, and deflections are available beginning in 2015-16.
Loose balls and box outs are available beginning in 2017-18.
The code is in [`hustle.py`](hustle.py)

### Play Type
These stats are all efficiency stats for different play types.
Availability for these stats begins in 2017-18.
Some players can have multiple rows if they changed teams mid-season, so extra code is needed to combine them.
The code is in [`playtype.py`](playtype.py)

### Game Started
This stat is not directly available (that I know of, at least) from stats.nba.com for whatever reason.
Instead, we have to calculate it by hand.
This is not too difficult because we already know the starters for each period for each game from the [`players_on_court.py`](../Possessions/players_on_court.py) file in the [`Possessions`](../Possessions) directory.
For that reason, running all scripts in the [`Possessions`](../Possessions) directory is required before calculating the games started.

## Combining All Stats
The last step is to combine all the different kinds of stats into a single table. 
I also rename the columns to make them consistent and easier to understand. 
The code for this is in [`combined.py`](combined.py).
There is also code to adjust combined stats for rate (possessions, games, minutes).