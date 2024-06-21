import pickle
import pandas as pd
from sklearn.decomposition import PCA
from feature_selection import *


# Perform Principal Component Analysis to reduce the number of dimensions
def reduce_dimensions_pca(data, num_dim):
    # Perform PCA
    pca = PCA(n_components=num_dim)
    pca.fit_transform(data)

    # Get the variance explained by each principal component
    explained_variance_ratio = pca.explained_variance_ratio_
    cumulative_explained_variance = explained_variance_ratio.cumsum()

    # Print the variance explained
    for i, (variance, cumulative) in enumerate(zip(explained_variance_ratio, cumulative_explained_variance), start=1):
        print(f"Principal Component {i}: Explained Variance = {variance:.4f}, "
              f"Cumulative Explained Variance = {cumulative:.4f}")

    return pca


if __name__ == '__main__':
    seasons = range(2017, 2024)
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

    # Reduce the dimensionality of the stats using PCA
    num_dim = 25
    principal_components = reduce_dimensions_pca(stats, num_dim)

    # Save principal components
    with open(f'Principal Components/{seasons[0]}_{num_dim}.pkl', 'wb') as fp:
        pickle.dump(principal_components, fp)
