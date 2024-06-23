# NBA-All-In-One
This repository is a tutorial project for creating a new all-in-one NBA statistic from scratch using Python.
The process used in this project was the result of comprehensive research into the techniques and practices used in the best publicly available models.
Links to resources I found helpful can be found in [Appendix A](#a-helpful-resources). 
The steps in the process are:
- Downloading play-by-play data from stats.nba.com
- Parsing play-by-play data to create possessions
- Using possessions to calculate regularized adjusted plus-minus (RAPM)
- Downloading stats from stats.nba.com
- Creating a statistical plus-minus (SPM) model that predicts a player's RAPM based on stats (not plus-minus)
- Using the SPM model as a prior in a new RAPM model
- Finding unique offensive roles for players based on stats
- Stabilizing small sample sizes with averages based on offensive role
- Adjusting plus-minus data for luck (shooting variance)

## Appendix
### A: Helpful Resources
Techniques
- [Luck Adjustment](https://fansided.com/2018/01/08/nylon-calculus-calculating-luck-adjusted-ratings/)
- Archetypes/Roles
  - [Nylon Calculus 1](https://fansided.com/2017/08/09/nylon-calculus-ranking-best-worst-scorers-every-offensive-role/)
  - [RotoGrinders](https://rotogrinders.com/pages/nba-defense-vs-archetype-overview-2703460)
  - [Nylon Calculus 2](https://fansided.com/2019/05/29/nylon-calculus-grouping-players-offensive-role-again/)
  - [Basketball Index](https://www.bball-index.com/offensive-archetypes/)
- Stabilization
  - [Kuder-Richardson 21](https://fansided.com/2014/08/29/long-take-three-point-shooting-stabilize/)
  - [Pearson Correlation Coefficient](https://fansided.com/2017/12/21/nylon-calculus-team-stats-noise-stabilization-thunder/)
  - [Padding](https://kmedved.com/2020/08/06/nba-stabilization-rates-and-the-padding-approach/)

Tutorials
- [RAPM Example](https://squared2020.com/2017/09/18/deep-dive-on-regularized-adjusted-plus-minus-i-introductory-example/)
- [Variety of super helpful Python tutorials courtesy of Ryan Davis](https://github.com/rd11490/NBA_Tutorials)
- [Jerermias Engelmann Python RAPM code](https://github.com/jerryengelmann/RAPM)
- [Andrew Patton tutorials](https://github.com/anpatton/basic-nba-tutorials)

Data
- [stats.nba.com API documentation](http://nbasense.com/nba-api/)
- [Public possessions data](https://www.pbpstats.com/)

Inspirations
- [LEBRON](https://www.bball-index.com/lebron-introduction/) 
- [RAPM](https://fansided.com/2014/09/25/glossary-plus-minus-adjusted-plus-minus/)
- [PIPM](https://www.bball-index.com/player-impact-plus-minus/)
- [DARKO](https://apanalytics.shinyapps.io/DARKO/)
- [EPM](https://dunksandthrees.com/about/epm)
- [BPM](https://www.basketball-reference.com/about/bpm2.html)
- [PTPM](https://counting-the-baskets.typepad.com/my-blog/2014/09/introducing-player-tracking-plus-minus.html)
- [SPI](https://nbacouchside.net/2022/11/05/introducing-nba-stable-player-impact-spi/)
- RPM (no longer available)
- RAPTOR (no longer available)