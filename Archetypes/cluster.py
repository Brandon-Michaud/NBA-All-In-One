import pandas as pd
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
import matplotlib.pyplot as plt
from dimensionality_reduction import *


# Create an elbow plot for k-means clustering
def elbow_plot_kmeans(data, max_clusters, save_filename, seed=42):
    # Compute the WCSS for different numbers of clusters
    wcss = []
    for i in range(1, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, random_state=seed)
        kmeans.fit(data)
        wcss.append(kmeans.inertia_ / data.shape[0])

    # Plot the elbow graph
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_clusters + 1), wcss, marker='o')
    plt.title('Elbow Plot For Optimal k')
    plt.xlabel('Number of Clusters')
    plt.ylabel('WCSS')
    plt.savefig(save_filename)


# Find clusters of players based on stats using k-means clustering
def get_clusters_kmeans(data, n_clusters, seed=42):
    # Apply k-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=seed)
    kmeans.fit(data)

    return kmeans


# Predict clusters for players based on stats using k-means clustering
def predict_clusters_kmeans(data, kmeans):
    # Predict cluster for each player
    clusters = kmeans.predict(data)

    return clusters


# Create an elbow plot for Gaussian mixture model
def elbow_plot_gmm(data, max_clusters, save_filename, seed=42):
    # Compute the BIC for different numbers of clusters
    bic = []
    for i in range(1, max_clusters + 1):
        print(i)
        gmm = GaussianMixture(n_components=i, random_state=seed)
        gmm.fit(data)
        bic.append(gmm.bic(data))

    # Plot the elbow graph
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, max_clusters + 1), bic, marker='o')
    plt.title('Elbow Method For Optimal Number of Clusters')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Bayesian Information Criterion')
    plt.savefig(save_filename)


# Find clusters of players based on stats using a Gaussian mixture model
def get_clusters_gmm(data, n_clusters, seed=42):
    # Fit the Gaussian Mixture Model
    gmm = GaussianMixture(n_components=n_clusters, random_state=seed)
    gmm.fit(data)

    return gmm


# Predict clusters for players based on stats using a Gaussian mixture model
def predict_clusters_gmm(data, gmm, hard=False):
    # Predict cluster for each player
    if hard:
        clusters = gmm.predict(data)
    else:
        clusters = gmm.predict_proba(data)

    return clusters


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
    player_ids = stats[['PLAYER_ID', 'SEASON', 'SEASON_TYPE']]
    stats = stats[input_features]

    # Load principal components
    with open(f'Principal Components/pcs_{seasons[0]}.pkl', 'rb') as fp:
        principal_components = pickle.load(fp)

    # Reduce dimensionality of stats using principal components
    n_components = 15
    reduced_stats = reduce_dimensions(stats, principal_components, n_components)

    # Create elbow plots to find optimal number of clusters
    max_clusters = 15
    elbow_plot_kmeans(reduced_stats, max_clusters, f'Clusters/Kmeans/elbow_{seasons[0]}_{n_components}.png')
    # elbow_plot_gmm(reduced_stats, max_clusters, f'Clusters/GMM/elbow_{seasons[0]}_{n_components}.png')

    # # Get clusters based on reduced stats
    # n_clusters = 9
    # # clusters = get_clusters_kmeans(reduced_stats, n_clusters)
    # clusters = get_clusters_gmm(reduced_stats, n_clusters)
    #
    # # Save clusters for later use
    # # with open(f'Clusters/Kmeans/{seasons[0]}_{n_components}.pkl', 'wb') as fp:
    # #     pickle.dump(clusters, fp)
    # with open(f'Clusters/GMM/{seasons[0]}_{n_components}.pkl', 'wb') as fp:
    #     pickle.dump(clusters, fp)
    #
    # # Load saved clusters
    # # with open(f'Clusters/Kmeans/{seasons[0]}_{n_components}.pkl', 'rb') as fp:
    # #     clusters = pickle.load(fp)
    # with open(f'Clusters/GMM/{seasons[0]}_{n_components}.pkl', 'rb') as fp:
    #     clusters = pickle.load(fp)
    #
    # # Predict clusters for each player
    # # predicted_clusters = predict_clusters_kmeans(reduced_stats, clusters)
    # predicted_clusters = predict_clusters_gmm(reduced_stats, clusters, hard=False)
    #
    # result = pd.concat([player_ids, stats], axis=1)
    # # result['CLUSTER'] = predicted_clusters
    # for i in range(n_clusters):
    #     result[f'CLUSTER_{i}_PROB'] = predicted_clusters[:, i]
    # player_names_and_ids = pd.read_csv('../Data/players_and_ids.csv')
    # result = player_names_and_ids.merge(result, on='PLAYER_ID', how='right')
    # result.to_csv('test.csv', index=False)
