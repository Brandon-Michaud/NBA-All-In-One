import pymc as pm
import pandas as pd

from rapm_helpers import *


# Create a Bayesian model and find RAPM values using maximum a posteriori estimation
def make_map_model(train_x, train_y):
    basic_model = pm.Model()
    with basic_model:
        alpha = pm.Normal('alpha', mu=1.1, sigma=0.1)
        # beta = pm.ExGaussian('beta', mu=-1.8, sigma=1, nu=2, shape=(train_x.shape[1],))
        beta = pm.Normal("beta", 0, 0.02, shape=(np.shape(train_x)[1],))
        mu = alpha + pm.math.dot(train_x, beta)
        y_obs = pm.Normal('y_obs', mu=mu, observed=train_y)
        idata = pm.find_MAP()
    return idata


# Extract coefficients from the model
def extract_coefficients_for_players_map(model, stat_name, unique_ids, include_ranks=False):
    # Convert unique player IDs from vector to matrix
    unique_ids_vector = np.array(unique_ids).reshape((len(unique_ids), 1))

    # Extract offensive and defensive coefficients
    coef = model['beta']
    coef_o = coef[0:len(unique_ids)].reshape((len(unique_ids), 1))
    coef_d = coef[len(unique_ids):].reshape((len(unique_ids), 1))

    # Concatenate player IDs with respective offensive and defensive coefficients
    id_with_coef = np.concatenate([unique_ids_vector, coef_o, coef_d], axis=1)

    # Convert matrix to data frame
    players_coef = pd.DataFrame(id_with_coef)

    # Apply new column names
    players_coef.columns = ['PLAYER_ID', f'O-{stat_name}', f'D-{stat_name}']

    # Calculate sum of offensive and defensive coefficients
    players_coef[stat_name] = players_coef[f'O-{stat_name}'] + players_coef[f'D-{stat_name}']

    # Rank players by coefficients
    if include_ranks:
        players_coef['{0}_Rank'.format(stat_name)] = players_coef[stat_name].rank(ascending=False)
        players_coef['O-{0}_Rank'.format(stat_name)] = players_coef['O-{0}'.format(stat_name)].rank(ascending=False)
        players_coef['D-{0}_Rank'.format(stat_name)] = players_coef['D-{0}'.format(stat_name)].rank(ascending=False)

    return players_coef


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season']
    all_possessions_filename = '../Data/Possessions/Standard/possessions_all.csv'
    players_and_ids_filename = '../Data/players_and_ids.csv'

    possessions = pd.read_csv(all_possessions_filename)
    player_names_and_ids = pd.read_csv(players_and_ids_filename)

    possessions = possessions[possessions['season'] == '2023-24'].iloc[:10000].copy()

    # Find unique player IDs
    unique_ids = find_unique_ids(possessions)

    # Calculate the points per 100 possessions
    possessions[points_per_100_column] = 100 * possessions[points_column].values / possessions[
        possessions_column].values

    # Create training set for the model
    train_x, train_y, num_possessions = create_training_set(possessions, points_per_100_column, unique_ids)

    # Create ridge regression model
    model = make_map_model(train_x.todense(), train_y)

    # Get the RAPM values for every player
    rapms = extract_coefficients_for_players_map(model, 'RAPM', unique_ids)

    # Merge with player names to provide insight beyond just player ID
    rapms = player_names_and_ids.merge(rapms, how='inner', on=player_id)

    # Round the values for ease of reading
    rapms = np.round(rapms, decimals=3)

    # Save RAPM values to a .csv file
    rapms.to_csv('test.csv', index=False)
