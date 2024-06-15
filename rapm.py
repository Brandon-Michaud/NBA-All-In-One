import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV


# Get sorted list of unique player IDs from the possessions data
def find_unique_ids(possessions):
    players = list(set(
        list(possessions['offensePlayer1Id'].unique()) + list(possessions['offensePlayer2Id'].unique()) +
        list(possessions['offensePlayer3Id'].unique()) + list(possessions['offensePlayer4Id'].unique()) +
        list(possessions['offensePlayer5Id'].unique()) + list(possessions['defensePlayer1Id'].unique()) +
        list(possessions['defensePlayer2Id'].unique()) + list(possessions['defensePlayer3Id'].unique()) +
        list(possessions['defensePlayer4Id'].unique()) + list(possessions['defensePlayer5Id'].unique())
    ))
    players.sort()
    return players


# Create a one-hot encoded row in the training matrix from the sparse encoded row in the possessions matrix
def create_training_row(row_in, unique_ids):
    # Initialize every player to 0, indicating they were not in
    row_out = np.zeros(len(unique_ids) * 2)

    # If player was on offense, set to 1
    for i in range(5):
        row_out[unique_ids.index(row_in[i])] = 1

    # If player was on defense, set to -1
    for i in range(5, 10):
        row_out[unique_ids.index(row_in[i]) + len(unique_ids)] = -1

    return row_out


# Create the one-hot encoded training set from the possessions data
def create_training_set(possessions, target_column, unique_ids):
    # Get the sparse encodings for the player IDs from the possessions data
    stints_x = possessions[['offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id', 'offensePlayer4Id',
                            'offensePlayer5Id', 'defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id',
                            'defensePlayer4Id', 'defensePlayer5Id']].to_numpy()

    # Convert each possession to a one-hot encoded row
    stints_x = np.apply_along_axis(create_training_row, 1, stints_x, unique_ids)

    # Get the target column
    stints_y = possessions[[target_column]].to_numpy()

    # Get the possessions column, necessary if using stints instead of single possessions
    possessions_vector = possessions['possessions']

    return stints_x, stints_y, possessions_vector


# Convert lambda value to alpha needed for ridge CV
def lambda_to_alpha(lambda_value, samples):
    return (lambda_value * samples) / 2.0


# Create a cross validation ridge regression model to fit data
def make_ridge_model(train_x, train_y, folds, weights, lambdas):
    # Convert lambdas to alphas
    alphas = [lambda_to_alpha(l, train_x.shape[0]) for l in lambdas]

    # Create a cross validation ridge regression model
    model = RidgeCV(alphas=alphas, cv=folds, fit_intercept=True)

    # Fit the training data
    fit_model = model.fit(train_x, train_y, sample_weight=weights)

    return fit_model


# Extract coefficients from the model
def extract_coefficients_for_players(model, stat_name, unique_ids, player_names_and_ids):
    # Convert unique player IDs from vector to matrix
    unique_ids_vector = np.array(unique_ids).reshape((len(unique_ids), 1))

    # Extract offensive and defensive coefficients
    coef_o = np.transpose(model.coef_[:, 0:len(unique_ids)])
    coef_d = np.transpose(model.coef_[:, len(unique_ids):])

    # Concatenate player IDs with respective offensive and defensive coefficients
    id_with_coef = np.concatenate([unique_ids_vector, coef_o, coef_d], axis=1)

    # Convert matrix to data frame
    players_coef = pd.DataFrame(id_with_coef)
    intercept = model.intercept_

    # Apply new column names
    players_coef.columns = ['playerId', f'{stat_name}__Off', f'{stat_name}__Def']

    # Calculate sum of offensive and defensive coefficients
    # TODO: Weigh sum by number of offensive and defensive possessions played. They are often not equal
    players_coef[stat_name] = players_coef[f'{stat_name}__Off'] + players_coef[f'{stat_name}__Def']

    # Rank players by coefficients
    players_coef['{0}_Rank'.format(stat_name)] = players_coef[stat_name].rank(ascending=False)
    players_coef['{0}__Off_Rank'.format(stat_name)] = players_coef['{0}__Off'.format(stat_name)].rank(ascending=False)
    players_coef['{0}__Def_Rank'.format(stat_name)] = players_coef['{0}__Def'.format(stat_name)].rank(ascending=False)

    # Add the intercept for reference
    players_coef[f'{stat_name}__Intercept'] = intercept[0]

    # Merge with player names to provide insight beyond just player ID
    players_coef = player_names_and_ids.merge(players_coef, how='inner', on='playerId')

    return players_coef


# Calculate RAPM from possessions data
def calculate_rapm(possessions, player_names_and_ids, folds, lambdas, save_file):
    # Find unique player IDs
    unique_ids = find_unique_ids(possessions)

    # Calculate the points per 100 possessions
    possessions['PointsPerPossession'] = 100 * possessions['points'].values / possessions['possessions'].values

    # Create training set for the model
    train_x, train_y, num_possessions = create_training_set(possessions, 'PointsPerPossession', unique_ids)

    # Create ridge regression model
    model = make_ridge_model(train_x, train_y, folds, num_possessions, lambdas)

    # Get the RAPM values for every player
    rapms = extract_coefficients_for_players(model, 'RAPM', unique_ids, player_names_and_ids)

    # Round the values for ease of reading
    rapms = np.round(rapms, decimals=3)

    # Sort the columns alphabetically
    rapms = rapms.reindex(sorted(rapms.columns), axis=1)

    # Save RAPM values to a .csv file
    rapms.to_csv(save_file)


if __name__ == '__main__':
    # Load data
    possessions = pd.read_csv('Data/rapm_possessions.csv')
    player_names_and_ids = pd.read_csv('Data/player_names.csv')

    # Filter out 0 possession possessions
    possessions = possessions[possessions['possessions'] > 0]

    # Test different lambda values
    lambdas = [0.01, 0.05, 0.1]

    # Calculate the RAPM values
    calculate_rapm(possessions, player_names_and_ids, 5, lambdas, 'Data/rapm.csv')
