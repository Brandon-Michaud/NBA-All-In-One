from sklearn.linear_model import RidgeCV
import pandas as pd
import numpy as np


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
def extract_coefficients_for_players_ridge(model, stat_name, unique_ids, include_ranks=False, include_intercept=False):
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
    players_coef[stat_name] = players_coef[f'O-{stat_name}'] + players_coef[f'D-{stat_name}']

    # Rank players by coefficients
    if include_ranks:
        players_coef['{0}_Rank'.format(stat_name)] = players_coef[stat_name].rank(ascending=False)
        players_coef['O-{0}_Rank'.format(stat_name)] = players_coef['O-{0}'.format(stat_name)].rank(ascending=False)
        players_coef['D-{0}_Rank'.format(stat_name)] = players_coef['D-{0}'.format(stat_name)].rank(ascending=False)

    # Add the intercept for reference
    if include_intercept:
        players_coef[f'{stat_name}_Intercept'] = intercept[0]

    return players_coef
