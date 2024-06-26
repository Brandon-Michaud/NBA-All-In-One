import pandas as pd


# Compare luck adjusted RAPM to basic RAPM for two RAPM files
def compare_luck_adjustment_with_basic(basic, luck_adjusted, save_filename):
    combined = basic.merge(luck_adjusted, on=['PLAYER_ID', 'PLAYER_NAME'], how='inner')
    combined['LA'] = combined['LA-RAPM'] - combined['RAPM']
    combined['O-LA'] = combined['O-LA-RAPM'] - combined['O-RAPM']
    combined['D-LA'] = combined['D-LA-RAPM'] - combined['D-RAPM']

    combined.to_csv(save_filename, index=False)


# Compare luck adjusted RAPM with basic RAPM or each range of seasons
def compare_luck_adjustment_with_basic_x_seasons(seasons, length, basic_filename, luck_adjusted_filename,
                                                 save_filename):
    # Compare luck adjusted RAPM with basic RAPM for each season
    for i in range(len(seasons) - length + 1):
        print(f'{((i + 1) / (len(seasons) - length + 1)):.2%}: {seasons[i]} to {seasons[i + length - 1]}')

        # Load basic RAPM and reorder columns
        basic = pd.read_csv(basic_filename.format(seasons[i], seasons[i + length - 1]))
        basic = basic[['PLAYER_ID', 'PLAYER_NAME', 'RAPM', 'O-RAPM', 'D-RAPM']]

        # Load luck-adjusted RAPM, reorder columns, and rename columns
        luck_adjusted = pd.read_csv(luck_adjusted_filename.format(seasons[i], seasons[i + length - 1]))
        luck_adjusted = luck_adjusted[['PLAYER_ID', 'PLAYER_NAME', 'RAPM', 'O-RAPM', 'D-RAPM']]
        luck_adjusted.columns = ['PLAYER_ID', 'PLAYER_NAME', 'LA-RAPM', 'O-LA-RAPM', 'D-LA-RAPM']

        # Compare luck adjusted RAPM with basic RAPM
        compare_luck_adjustment_with_basic(basic, luck_adjusted,
                                           save_filename.format(seasons[i], seasons[i + length - 1]))


# Add stats to RAPM table
def add_stats(rapm, stats, save_filename):
    # Add stats to RAPM table
    combined = rapm.merge(stats, on='PLAYER_ID', how='inner')

    # Save RAPM with stats to csv
    combined.to_csv(save_filename, index=False)


# Add stats to RAPM for each range of seasons
def add_stats_x_seasons(seasons, season_types, length, rapm_filename, stats_filename, save_filename):
    # Load stats for all seasons and get only relevant season types
    stats = pd.read_csv(stats_filename)
    stats = stats[stats['SEASON_TYPE'].isin(season_types)]

    # Add stats to RAPM for each range of seasons
    for i in range(len(seasons) - length + 1):
        print(f'{((i + 1) / (len(seasons) - length + 1)):.2%}: {seasons[i]} to {seasons[i + length - 1]}')

        # Load RAPM
        rapm = pd.read_csv(rapm_filename.format(seasons[i], seasons[i + length - 1]))

        # Get stats for seasons in range
        filtered_stats = stats[(stats['SEASON'] >= seasons[i]) & (stats['SEASON'] <= seasons[i + length - 1])]

        # Add stats to RAPM
        add_stats(rapm, filtered_stats, save_filename.format(seasons[i], seasons[i + length - 1]))


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season']
    basic_filename = '../Data/RAPM/Standard/Seasons/rapm_regular_season_{}_{}.csv'
    luck_adjusted_filename = '../Data/RAPM/LuckAdjusted/Seasons/rapm_regular_season_{}_{}.csv'
    compare_filename = '../Data/RAPM/Combined/Seasons/rapm_regular_season_{}_{}.csv'
    stats_filename = '../Data/SeasonStats/Combined/all_seasons_totals.csv'
    rapm_with_stats_filename = '../Data/RAPM/WithStats/Seasons/rapm_regular_season_{}_{}.csv'

    # compare_luck_adjustment_with_basic_x_seasons(seasons, 1, basic_filename, luck_adjusted_filename, compare_filename)
    add_stats_x_seasons(seasons, season_types, 1, compare_filename, stats_filename, rapm_with_stats_filename)
