import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV


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
    stints_x = possessions[offense_player_ids + defense_player_ids].to_numpy()

    # Convert each possession to a one-hot encoded row
    stints_x = np.apply_along_axis(create_training_row, 1, stints_x, unique_ids)

    # Get the target column
    stints_y = possessions[[target_column]].to_numpy()

    # Get the possessions column, necessary if using stints instead of single possessions
    possessions_vector = possessions[possessions_column]

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
def extract_coefficients_for_players(model, stat_name, unique_ids, player_names_and_ids, include_ranks=False,
                                     include_intercept=False):
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
    players_coef.columns = ['PLAYER_ID', f'O-{stat_name}', f'D-{stat_name}']

    # Calculate sum of offensive and defensive coefficients
    # TODO: Weigh sum by number of offensive and defensive possessions played. They are often not equal
    players_coef[stat_name] = players_coef[f'O-{stat_name}'] + players_coef[f'D-{stat_name}']

    # Rank players by coefficients
    if include_ranks:
        players_coef['{0}_Rank'.format(stat_name)] = players_coef[stat_name].rank(ascending=False)
        players_coef['O-{0}_Rank'.format(stat_name)] = players_coef['O-{0}'.format(stat_name)].rank(ascending=False)
        players_coef['D-{0}_Rank'.format(stat_name)] = players_coef['D-{0}'.format(stat_name)].rank(ascending=False)

    # Add the intercept for reference
    if include_intercept:
        players_coef[f'{stat_name}_Intercept'] = intercept[0]

    # Merge with player names to provide insight beyond just player ID
    players_coef = players_coef.merge(player_names_and_ids, how='inner', on=player_id)

    return players_coef


# Calculate RAPM from possessions data
def calculate_rapm(possessions, player_names_and_ids, folds, lambdas, save_file):
    # Find unique player IDs
    unique_ids = find_unique_ids(possessions)

    # Calculate the points per 100 possessions
    possessions[points_per_100_column] = 100 * possessions[points_column].values / possessions[possessions_column].values

    # Create training set for the model
    train_x, train_y, num_possessions = create_training_set(possessions, points_per_100_column, unique_ids)

    # Create ridge regression model
    model = make_ridge_model(train_x, train_y, folds, num_possessions, lambdas)

    # Get the RAPM values for every player
    rapms = extract_coefficients_for_players(model, 'RAPM', unique_ids, player_names_and_ids)

    # Round the values for ease of reading
    rapms = np.round(rapms, decimals=3)

    # Save RAPM values to a .csv file
    rapms.to_csv(save_file, index=False)


# Calculate RAPM over a custom range of seasons
def calculate_rapm_season_range(all_possessions, start_season, end_season, player_names_and_ids, folds, lambdas, save_file):
    # Get all possessions in season range
    possessions_in_range = all_possessions[(all_possessions['season'] >= start_season) &
                                           (all_possessions['season'] <= end_season)].copy()

    # Calculate RAPM over custom range
    calculate_rapm(possessions_in_range, player_names_and_ids, folds, lambdas, save_file)


# Calculate RAPM over a custom range of dates
def calculate_rapm_date_range(all_possessions, start_date, end_date, player_names_and_ids, folds, lambdas, save_file):
    # Get all possessions in date range
    possessions_in_range = all_possessions[(all_possessions['date'] >= start_date) &
                                           (all_possessions['date'] <= end_date)].copy()

    # Calculate RAPM over custom range
    calculate_rapm(possessions_in_range, player_names_and_ids, folds, lambdas, save_file)


# Calculate RAPM for each range of seasons
def calculate_x_season_rapms(all_possessions, seasons, season_types, length, player_names_and_ids, folds, lambdas, save_file):
    # Get possessions for corresponding season types
    all_possessions = all_possessions[all_possessions['season_type'].isin(season_types)]

    # Find RAPM for possessions for the current season range
    for i in range(len(seasons) - length + 1):
        print(f'{((i + 1) / (len(seasons) - length + 1)):.2%}: {seasons[i]} to {seasons[i + length - 1]}')
        calculate_rapm_season_range(all_possessions, seasons[i], seasons[i + length - 1], player_names_and_ids, folds,
                                    lambdas, save_file.format(seasons[i], seasons[i + length - 1]))


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season']
    all_possessions_filename = '../Data/Possessions/Standard/possessions_all.csv'
    players_and_ids_filename = '../Data/players_and_ids.csv'

    all_possessions = pd.read_csv(all_possessions_filename)
    player_names_and_ids = pd.read_csv(players_and_ids_filename)

    # Test different lambda values
    lambdas = [0.01, 0.05, 0.1]
    folds = 5

    calculate_x_season_rapms(all_possessions, seasons, season_types, 1, player_names_and_ids, folds, lambdas,
                             '../Data/RAPM/Standard/Seasons/rapm_regular_season_{}_{}.csv')
