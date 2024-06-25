import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from feature_selection import *


# Perform Principal Component Analysis to find the principal components
def find_principal_components(data, n_components, verbose=False, elbow_plot_savefile=None):
    # Perform PCA
    pca = PCA(n_components=n_components)
    pca.fit_transform(data)

    # Get the variance explained by each principal component
    explained_variance_ratio = pca.explained_variance_ratio_
    cumulative_explained_variance = explained_variance_ratio.cumsum()

    # Print the variance explained
    if verbose:
        # Plot the explained variance ratio
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(pca.explained_variance_ratio_) + 1), pca.explained_variance_ratio_.cumsum(), marker='o')
        plt.xlabel('Number of Principal Components')
        plt.ylabel('Cumulative Explained Variance')
        plt.title('Explained Variance by Principal Components')
        plt.grid(True)
        plt.savefig(elbow_plot_savefile)

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
    seasons = range(1996, 2024)
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
    principal_components = find_principal_components(stats, 50, verbose=True,
                                                     elbow_plot_savefile=f'Principal Components/elbow_{seasons[0]}.png')

    # Save principal components
    with open(f'Principal Components/pcs_{seasons[0]}.pkl', 'wb') as fp:
        pickle.dump(principal_components, fp)
