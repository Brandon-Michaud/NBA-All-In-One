from rapm_helpers import *
from ridge import *


# Calculate RAPM from possessions data
def calculate_rapm(possessions, player_names_and_ids, folds, lambdas, save_file):
    # Find unique player IDs
    unique_ids = find_unique_ids(possessions)

    # Calculate the points per 100 possessions
    possessions[points_per_100_column] = 100 * possessions[points_column].values / possessions[possessions_column].values

    # Create training set for the model
    train_x, train_y, num_possessions = create_training_set(possessions, points_per_100_column, unique_ids)

    # Create ridge regression model
    model = make_ridge_model(train_x.tocsr(), train_y, folds, num_possessions, lambdas)

    # Get the RAPM values for every player
    rapms = extract_coefficients_for_players_ridge(model, 'RAPM', unique_ids)

    # Merge with player names to provide insight beyond just player ID
    rapms = player_names_and_ids.merge(rapms, how='inner', on=player_id)

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
