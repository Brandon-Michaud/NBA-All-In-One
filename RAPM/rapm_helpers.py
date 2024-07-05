import numpy as np
from scipy.sparse import lil_matrix

# Constants used for column names
offense_player_id = 'offensive_player{}'
defense_player_id = 'defensive_player{}'
offense_player_ids = [offense_player_id.format(i) for i in range(1, 6)]
defense_player_ids = [defense_player_id.format(i) for i in range(1, 6)]
points_column = 'points'
possessions_column = 'possessions'
points_per_100_column = 'points_per_100'
player_id = 'PLAYER_ID'


# Get sorted list of unique player IDs from the possessions data
def find_unique_ids(possessions):
    players = list(set(
        list(possessions[offense_player_id.format(1)].unique()) + list(possessions[offense_player_id.format(2)].unique()) +
        list(possessions[offense_player_id.format(3)].unique()) + list(possessions[offense_player_id.format(4)].unique()) +
        list(possessions[offense_player_id.format(5)].unique()) + list(possessions[defense_player_id.format(1)].unique()) +
        list(possessions[defense_player_id.format(2)].unique()) + list(possessions[defense_player_id.format(3)].unique()) +
        list(possessions[defense_player_id.format(4)].unique()) + list(possessions[defense_player_id.format(5)].unique())
    ))
    players.sort()
    return players


# Create a sparse encoded row in the training matrix from the possessions matrix
def create_training_row(row_in, unique_ids):
    # Initialize a sparse row for efficiency
    row_out = lil_matrix((1, len(unique_ids) * 2))

    # If player was on offense, set to 1
    for i in range(5):
        row_out[0, unique_ids.index(row_in[i])] = 1

    # If player was on defense, set to -1
    for i in range(5, 10):
        row_out[0, unique_ids.index(row_in[i]) + len(unique_ids)] = -1

    return row_out


# Create the one-hot encoded training set from the possessions data
def create_training_set(possessions, target_column, unique_ids):
    # Get the sparse encodings for the player IDs from the possessions data
    stints_x = possessions[offense_player_ids + defense_player_ids].to_numpy()

    # Convert each possession to a sparse one-hot encoded row
    stints_x_sparse = lil_matrix((stints_x.shape[0], len(unique_ids) * 2))
    for i in range(stints_x.shape[0]):
        stints_x_sparse[i, :] = create_training_row(stints_x[i, :], unique_ids)

    # Get the target column
    stints_y = possessions[[target_column]].to_numpy()

    # Get the possessions column, necessary if using stints instead of single possessions
    possessions_vector = possessions[possessions_column].to_numpy()

    return stints_x_sparse, stints_y, possessions_vector
