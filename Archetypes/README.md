# Archetypes
This directory handles learning offensive archetypes of NBA players based on the stats downloaded in the [`Stats`](../Stats) directory.

## Steps
### 1: Feature Selection
There are a very large number of stats available, but the curse of dimensionality requires significant feature reduction.
Some of this reduction is handled in [`feature_selection.py`](feature_selection.py).
In this file, I manually remove some stats that were clearly unhelpful for finding offensive archetypes (defensive stats, wins, games played, etc.).
I also wrote functions that use statistical methods (R^2 and VIF) to find highly correlated columns and the user can decide whether to keep or remove either of them.
For these methods to work, the data must be standardized, so there are functions that accomplish this as well.
The computer-aided selected features are stored in a pickle file for later use.

### 2: Dimensionality Reduction
I found that, even after removing redundant columns, there were still far too many features for a clustering model to be useful.
Thus, the next step is to use Principal Component Analysis to find the principal components of the data.
These are linear combinations of the features which explain the most variance in the data. 
This code is found in [`dimensionality_reduction.py`](dimensionality_reduction.py). 
The code to find the principal components can also produce an elbow plot of the cumulative percentage of the variance explained for each principal component.
This is useful for selecting the number of principal components to use as features.

### 3: Clustering (WIP)
The final step is to use the principal component features to find clusters of players, which in this application are offensive archetypes.
This is a classic unsupervised learning problem.
There are several different machine learning algorithms that can do this.
Right now, I have included code for k-means clustering and Gaussian mixture models, 
but I intend to continue iterating upon these models and adding new ones to see what works best.