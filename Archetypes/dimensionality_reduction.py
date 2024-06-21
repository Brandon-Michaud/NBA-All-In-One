import pickle
import pandas as pd
from sklearn.decomposition import PCA
from feature_selection import *


# Perform Principal Component Analysis to find the principal components
def find_principal_components(data, n_components, verbose=False):
    # Perform PCA
    pca = PCA(n_components=n_components)
    pca.fit_transform(data)

    # Get the variance explained by each principal component
    explained_variance_ratio = pca.explained_variance_ratio_
    cumulative_explained_variance = explained_variance_ratio.cumsum()

    # Print the variance explained
    if verbose:
        for i, (variance, cumulative) in enumerate(zip(explained_variance_ratio, cumulative_explained_variance)):
            print(f"Principal Component {i + 1}: Explained Variance = {variance:.4f}, "
                  f"Cumulative Explained Variance = {cumulative:.4f}")

    return pca


# Reduce the number of dimensions using principal components
def reduce_dimensions(data, principal_components, n_use):
    # Transform the data using the principal components
    reduced_data = principal_components.transform(data)

    # Select subset of principal components
    reduced_data = reduced_data[:, :n_use]

    # Convert to dataframe
    reduced_data_df = pd.DataFrame(reduced_data, columns=[f'PC{i + 1}' for i in range(n_use)])

    return reduced_data_df


if __name__ == '__main__':
    seasons = range(2015, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']

    # Load standardized stats for all seasons
    stats = pd.read_csv('../Data/SeasonStats/Combined/all_seasons_standardized.csv')

    # Get only rows in seasons range
    stats = stats[(stats['SEASON'].isin(seasons)) & (stats['SEASON_TYPE'].isin(season_types))]

    # Load features chosen
    with open('chosen_features.pkl', 'rb') as fp:
        chosen_inputs = pickle.load(fp)

    # Only use chosen features if they are available
    input_features = get_available_chosen_columns(seasons[0], chosen_inputs)
    stats = stats[input_features]

    # Find principal components
    n_components = 25
    # principal_components = find_principal_components(stats, n_components, verbose=True)
    #
    # # Save principal components
    # with open(f'Principal Components/{seasons[0]}_{n_components}.pkl', 'wb') as fp:
    #     pickle.dump(principal_components, fp)

    # Load principal components
    with open(f'Principal Components/{seasons[0]}_{n_components}.pkl', 'rb') as fp:
        principal_components = pickle.load(fp)

    reduced_stats = reduce_dimensions(stats, principal_components, 15)
    reduced_stats.to_csv('test.csv', index=False)
