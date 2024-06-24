# Possessions
This directory handles downloading play-by-play data and parsing it for possessions.
Much of this code is adapted from [Ryan Davis' GitHub tutorial](https://github.com/rd11490/NBA_Tutorials).
The key differences are:
- My code is structured in a way that allows the files to be imported into other Python files and used.
- My code extends the single game examples from Ryan Davis to multiple games.
- I fixed a few issues I noticed with parsing possessions.
- I added extra documentation in the form of comments to the code.

## Steps
### 0: Set Up Response Handling
To download data from stats.nba.com, very specific request headers are needed.
The data used in this project is also returned as JSON objects which represent tables.
The code for handling requests and responses is found in [`api_helpers.py`](../api_helpers.py).
This code is also used in other directories, so it is on the same level as the [`Possessions`](../Possessions) directory in the file tree.

### 1: Download Play-by-Play Data
The first step is to download all the play-by-play for every game for every season since 1996-97.
This is the first season play-by-play data is available through stats.nba.com.
The functions to do this are inside [`download_play_by_play.py`](download_play_by_play.py). 
Any failed downloads will be stored as dictionaries in pickle files so that they can be evaluated and retried.
In my experiences it is not uncommon for a few downloads to fail for no apparent reason.
Retrying usually fixes the issue.

### 2: Find Starters For Each Period
The next step is to parse the play-by-play data to find the starters for each team for each period for each game.
This is necessary because there is no event in the play-by-play data detailing who began the period on the court.
Substitutions made in between periods are also not documented, hence why starters are calculated for all periods.

There are two ways of doing this:
1. Parse the play-by-play files to find every player who recorded an event and was subbed out before they were subbed in or not subbed at all.
This works for the vast majority of games, but it fails when a player does not record a single event for an entire period and is never subbed out.
2. For the games that the first method fails, box scores for each period can be downloaded.
These box scores will include players even if they did not record an event for the whole period. 
The same methodology of the first method is used, but now players who did not record an event are known.

The first method is preferred because it does not have to make any additional requests, making it much faster.
The code for both methods is in [`players_on_court.py`](players_on_court.py).
There are some play-by-play files that have human errors and thus cannot be parsed algorithmically.
A list of these I found and how I handled them can be found in [Appendix A](#a-play-by-play-errors).
Once again, failed games are saved to pickle files so that they can be analyzed and retried.
More fine-grained details can be found in the comments of the code itself.

### 3: Find Possessions
The next step is to determine possessions from the play-by-play data.
A possession ends when:
- A shot is made that is not an And-1
- A final free throw is made that results in change of possession (i.e. not an away from play, inbounds, etc.)
- A defensive rebound is made
- A turnover is committed
- The period ends

[`play_by_play_helpers.py`](play_by_play_helpers.py) is used to help classify events from the play-by-play data. 
[`make_possessions.py`](make_possessions.py) uses these play-by-play events to determine possessions.
It also keeps track of who was on the floor for each possession using the starters for each period found in the previous step along with the substitutions in the play-by-play.
Detailed specifics can be found in the comments of the code.

There are, again, some human errors in the play-by-play data that cause issues for the possessions finder.
The issue is usually with the substitutions being wrong.
A list of issues I found and how I handled them can be found in [Appendix B](#b-possessions-errors).
Any failed games will be stored in a pickle file.

### 4: Combine Possessions
The final step is to combine all possessions for all seasons.
This includes reformatting the data in a way that is more easily handled in future RAPM calculations.
The code for this step is in [`combine_possessions.py`](combine_possessions.py).

### 5: Find All Players' IDs
An additional step I take is to keep track of the name belonging to each player ID.
This is helpful when looking at RAPM results.
The code for this step is in [`players_and_ids.py`](players_and_ids.py).
It just goes through every single play-by-play file and looks for new player IDs to add to the list.

## Appendix
### A: Play-by-Play Errors
Each game is represented by the game ID from stats.nba.com. 
Numbers inside parentheses are player IDs.
- 0029600657
	- Spurs vs Kings, February 3, 1997
	- Substitution at 5:44 in period 2 seems to be an error
	- Duplicate sub is made at 4:54 in period 2, so I think there was a typo
	- Remove sub at 5:44
- 0029601150
	- SuperSonics vs Spurs, April 15, 1997
	- Hawkins (765) is subbed in and out at the same time at 4:55 in period 3
	- In reality, Hawkins never leaves the game
	- Real sub should be Perkins (64) for Cummings (187)
- 0029600175
	- Timberwolves at Bullets, November 25, 1996
	- Chris Carr (713) is said to have taken a shot at 0:22 in period 3, but I do not believe he was actually in the game according to the play-by-play
	- Could be that Carr was subbed in, but the sub was never recorded
	- Remove entire period
- 0029700438
	- SuperSonics vs 76ers, January 2, 1998
	- Jim McIlvaine (29) is credited with a rebound at 1:50 in period 2, but I do not believe he was in the game
	- There is significant reason to believe that subs are missing in the play-by-play
	- Remove entire period
- 0029701045
	- Warriors vs Bucks, March 31, 1998
	- Jason Caffey (679) entered the game for Eric Dampier (956) before a free throw at 0:22 in period 5, the free throw was made, a timeout was called, and Caffey left the game. 
	- The original sub was added after the fact and has a higher EVENTNUM than the second sub
	- Change the first sub EVENTNUM to be smaller than the second sub EVENTNUM to fix the issue
- 0029701075
	- Celtics vs Knicks, April 5, 1998
	- Tyus Edney (721) was credited with a turnover at 2:23 in period 3, but I do not think he was in the game
	- 7 players played for Knicks in period 3, but no substitutions are listed
	- Remove entire period
- 0029700452
	- SuperSonics at Grizzlies, January 4, 1998
	- Seems like a sub was forgotten for SuperSonics in period 3
	- Remove entire period
- 0020100018
	- Wizards at Hawks, November 1, 2001
	- Whitney (43) is subbed in and out at the same time at 7:47 in period 4
	- I do not think either sub is correct
	- Delete both subs
- 0020400335
	- Hornets vs Spurs, December 17, 2004
	- Missing substitution Junior Harrington (2454) for J.R. Smith (2747) at 7:59 in period 2 according to Basketball Reference
- 0020500090
	- Celtics vs Rockets, November 13, 2005
	- Kendrick Perkins (2570) was subbed in on a free throw at 1:27 in period 2. The free throw missed and a timeout was called still at 1:27 when Perkins was subbed out. 
    - The sub in has a larger EVENTNUM than the sub out, causing the issue
	- Change the EVENTNUM of the first sub to be smaller than the EVENTNUM of second sub to fix the issue
- 0021500707
	- Warriors at 76ers, January 30, 2016
	- Harrison Barnes (203084) was subbed in and out at the same time at 8:53 in period 4
	- I believe he remained in the game
	- His two subs should be changed to one sub Klay Thompson (202691) for Leandro Barbosa (2571)
- 0022200234
	- Lakers vs Pistons, November 18, 2022
	- Dennis Schroder (203471) is subbed out at 8:51 in period 2 and again at 7:08 without ever being subbed back in
	- Sub at 7:08 should be deleted because Kendrick Nunn (1629134) was already in the game according to ESPN
- 0022201040
	- Mavericks at Spurs, March 15, 2023
	- Bullock was subbed out on a free throw at 0:03 in period 4 and then subbed back in after the free throw still at 0:03. 
    - The sub out has a higher EVENTNUM, causing the issue
	- Change the EVENTNUM of the first sub to be smaller than the EVENTNUM of second sub to fix the issue
- 0021500916
	- Raptors vs Blazers, March 4, 2016
	- For some reason there is a start of overtime event even though the game did not go to overtime
	- Delete start of overtime event

### B: Possessions Errors
Each game is represented by the game ID from stats.nba.com. 
Numbers inside parentheses are player IDs.
- 0029600370
	- SuperSonics vs Mavericks, December 22, 1996
	- Last event of period 4 is marked as a made shot, but the neutral description says no shot
	- Missing end of period event for period 4
	- Several events are missing because the last event says the final score was 76-91, but the actual score was 79-93
	- Add end of period event and concede that we are missing the last 39 seconds of play by play
- 0029700159
	- Nuggets at Grizzlies, 
	- There seems to be confusion with Nuggets subs at 3:08 and 1:51 in period 3
	- I can't decipher what the correct subs should be.
    - Delete the entire period
- 0020000883
	- Suns vs Kings,
	- There is an empty substitution event at 0:46 in period 4
	- Delete event
- 0020101009
	- Pistons at Pacers,
	- Nonsense going on with ejections at 1:16 in period 4
	- Alexander (2349) actually entered the game for Williamson (722) because Williamson was ejected
	- Foster (1902) actually entered the game for O'Neal (979) because O'Neal was ejected
- 0021700482
	- Nets at Pacers,
	- General nonsense going on with Nets subs at 0:00 in period 5
	- Everything I tried did not fix the issue.
    - Delete the entire period
- 0022000853
	- Trail Blazers at Spurs, April 16, 2021
	- Duplicate subs by Trail Blazers at 9:26 and 8:13 in period 3
	- The first sub is wrong according to Basketball Reference and ESPN, so remove it