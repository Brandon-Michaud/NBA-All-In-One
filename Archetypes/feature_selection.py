import pandas as pd
import pickle
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

from Stats.combined import (get_availability, track_types, general_measure_types,
                            play_types, play_type_defenses, defense_categories, distance_ranges)

# Manual feature selection
# We want to find offensive archetypes, so we need to remove columns which do not capture this
# - No defensive (or partially defensive) stats needed
# - Advanced stats like offensive rating do not provide much useful information about role
# - All stats will be per 100 possessions, so no need for possessions
# - Assist ratio is assists per 100 possessions, which we already have
# - Role typically diminishes with age, but we want to discover this from the other stats, not age itself
# - Games played and wins do not help identify role
manual_inputs_map = {
    'Box Outs': ['O_BOX_OUTS'],
    'Defense': {
        '2 Pointers': [],
        '3 Pointers': [],
        'Greater Than 15Ft': [],
        'Less Than 6Ft': [],
        'Less Than 10Ft': [],
        'Overall': [],
    },
    'General': {
        'Advanced': ['AST_PCT', 'AST_TO', 'OREB_PCT', 'TM_TOV_PCT', 'EFG_PCT', 'TS_PCT', 'USG_PCT', 'PACE'],
        'Base': ['MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'AST', 'TOV', 'PTS'],
        'Defense': [],
        'Misc': ['PTS_OFF_TOV', 'PTS_2ND_CHANCE', 'PTS_FB', 'PTS_PAINT'],
        'Scoring': ['PCT_FGA_2PT', 'PCT_FGA_3PT', 'PCT_PTS_2PT', 'PCT_PTS_2PT_MR', 'PCT_PTS_3PT', 'PCT_PTS_FB', 'PCT_PTS_FT', 'PCT_PTS_OFF_TOV', 'PCT_PTS_PAINT', 'PCT_AST_2PM', 'PCT_UAST_2PM', 'PCT_AST_3PM', 'PCT_UAST_3PM', 'PCT_AST_FGM', 'PCT_UAST_FGM'],
        'Usage': ['PCT_TEAM_FGM', 'PCT_TEAM_FGA', 'PCT_TEAM_FG3M', 'PCT_TEAM_FG3A', 'PCT_TEAM_FTM', 'PCT_TEAM_FTA', 'PCT_TEAM_OREB', 'PCT_TEAM_AST', 'PCT_TEAM_TOV', 'PCT_TEAM_PTS'],
    },
    'Hustle': ['SCREEN_ASSISTS', 'SCREEN_AST_PTS', 'O_LOOSE_BALLS_RECOVERED'],
    'Play Types': {
        'Cut': {
            'offensive': ['O_CUT_PERCENTILE', 'O_CUT_POSS_PCT', 'O_CUT_PPP', 'O_CUT_FG_PCT', 'O_CUT_FT_POSS_PCT', 'O_CUT_TOV_POSS_PCT', 'O_CUT_SF_POSS_PCT', 'O_CUT_PLUSONE_POSS_PCT', 'O_CUT_SCORE_POSS_PCT', 'O_CUT_EFG_PCT', 'O_CUT_POSS', 'O_CUT_PTS', 'O_CUT_FGM', 'O_CUT_FGA', 'O_CUT_FGMX'],
            'defensive': [],
        },
        'Handoff': {
            'offensive': ['O_HANDOFF_PERCENTILE', 'O_HANDOFF_POSS_PCT', 'O_HANDOFF_PPP', 'O_HANDOFF_FG_PCT', 'O_HANDOFF_FT_POSS_PCT', 'O_HANDOFF_TOV_POSS_PCT', 'O_HANDOFF_SF_POSS_PCT', 'O_HANDOFF_PLUSONE_POSS_PCT', 'O_HANDOFF_SCORE_POSS_PCT', 'O_HANDOFF_EFG_PCT', 'O_HANDOFF_POSS', 'O_HANDOFF_PTS', 'O_HANDOFF_FGM', 'O_HANDOFF_FGA', 'O_HANDOFF_FGMX'],
            'defensive': [],
        },
        'Isolation': {
            'offensive': ['O_ISO_PERCENTILE', 'O_ISO_POSS_PCT', 'O_ISO_PPP', 'O_ISO_FG_PCT', 'O_ISO_FT_POSS_PCT', 'O_ISO_TOV_POSS_PCT', 'O_ISO_SF_POSS_PCT', 'O_ISO_PLUSONE_POSS_PCT', 'O_ISO_SCORE_POSS_PCT', 'O_ISO_EFG_PCT', 'O_ISO_POSS', 'O_ISO_PTS', 'O_ISO_FGM', 'O_ISO_FGA', 'O_ISO_FGMX'],
            'defensive': [],
        },
        'Misc': {
            'offensive': ['O_MISC_PERCENTILE', 'O_MISC_POSS_PCT', 'O_MISC_PPP', 'O_MISC_FG_PCT', 'O_MISC_FT_POSS_PCT', 'O_MISC_TOV_POSS_PCT', 'O_MISC_SF_POSS_PCT', 'O_MISC_PLUSONE_POSS_PCT', 'O_MISC_SCORE_POSS_PCT', 'O_MISC_EFG_PCT', 'O_MISC_POSS', 'O_MISC_PTS', 'O_MISC_FGM', 'O_MISC_FGA', 'O_MISC_FGMX'],
            'defensive': [],
        },
        'OffRebound': {
            'offensive': ['O_OFFREB_PERCENTILE', 'O_OFFREB_POSS_PCT', 'O_OFFREB_PPP', 'O_OFFREB_FG_PCT', 'O_OFFREB_FT_POSS_PCT', 'O_OFFREB_TOV_POSS_PCT', 'O_OFFREB_SF_POSS_PCT', 'O_OFFREB_PLUSONE_POSS_PCT', 'O_OFFREB_SCORE_POSS_PCT', 'O_OFFREB_EFG_PCT', 'O_OFFREB_POSS', 'O_OFFREB_PTS', 'O_OFFREB_FGM', 'O_OFFREB_FGA', 'O_OFFREB_FGMX'],
            'defensive': [],
        },
        'OffScreen': {
            'offensive': ['O_OFFSCREEN_PERCENTILE', 'O_OFFSCREEN_POSS_PCT', 'O_OFFSCREEN_PPP', 'O_OFFSCREEN_FG_PCT', 'O_OFFSCREEN_FT_POSS_PCT', 'O_OFFSCREEN_TOV_POSS_PCT', 'O_OFFSCREEN_SF_POSS_PCT', 'O_OFFSCREEN_PLUSONE_POSS_PCT', 'O_OFFSCREEN_SCORE_POSS_PCT', 'O_OFFSCREEN_EFG_PCT', 'O_OFFSCREEN_POSS', 'O_OFFSCREEN_PTS', 'O_OFFSCREEN_FGM', 'O_OFFSCREEN_FGA', 'O_OFFSCREEN_FGMX'],
            'defensive': [],
        },
        'Postup': {
            'offensive': ['O_POSTUP_PERCENTILE', 'O_POSTUP_POSS_PCT', 'O_POSTUP_PPP', 'O_POSTUP_FG_PCT', 'O_POSTUP_FT_POSS_PCT', 'O_POSTUP_TOV_POSS_PCT', 'O_POSTUP_SF_POSS_PCT', 'O_POSTUP_PLUSONE_POSS_PCT', 'O_POSTUP_SCORE_POSS_PCT', 'O_POSTUP_EFG_PCT', 'O_POSTUP_POSS', 'O_POSTUP_PTS', 'O_POSTUP_FGM', 'O_POSTUP_FGA', 'O_POSTUP_FGMX'],
            'defensive': [],
        },
        'PRBallHandler': {
            'offensive': ['O_PRBH_PERCENTILE', 'O_PRBH_POSS_PCT', 'O_PRBH_PPP', 'O_PRBH_FG_PCT', 'O_PRBH_FT_POSS_PCT', 'O_PRBH_TOV_POSS_PCT', 'O_PRBH_SF_POSS_PCT', 'O_PRBH_PLUSONE_POSS_PCT', 'O_PRBH_SCORE_POSS_PCT', 'O_PRBH_EFG_PCT', 'O_PRBH_POSS', 'O_PRBH_PTS', 'O_PRBH_FGM', 'O_PRBH_FGA', 'O_PRBH_FGMX'],
            'defensive': [],
        },
        'PRRollman': {
            'offensive': ['O_PRRM_PERCENTILE', 'O_PRRM_POSS_PCT', 'O_PRRM_PPP', 'O_PRRM_FG_PCT', 'O_PRRM_FT_POSS_PCT', 'O_PRRM_TOV_POSS_PCT', 'O_PRRM_SF_POSS_PCT', 'O_PRRM_PLUSONE_POSS_PCT', 'O_PRRM_SCORE_POSS_PCT', 'O_PRRM_EFG_PCT', 'O_PRRM_POSS', 'O_PRRM_PTS', 'O_PRRM_FGM', 'O_PRRM_FGA', 'O_PRRM_FGMX'],
            'defensive': [],
        },
        'Spotup': {
            'offensive': ['O_SPOTUP_PERCENTILE', 'O_SPOTUP_POSS_PCT', 'O_SPOTUP_PPP', 'O_SPOTUP_FG_PCT', 'O_SPOTUP_FT_POSS_PCT', 'O_SPOTUP_TOV_POSS_PCT', 'O_SPOTUP_SF_POSS_PCT', 'O_SPOTUP_PLUSONE_POSS_PCT', 'O_SPOTUP_SCORE_POSS_PCT', 'O_SPOTUP_EFG_PCT', 'O_SPOTUP_POSS', 'O_SPOTUP_PTS', 'O_SPOTUP_FGM', 'O_SPOTUP_FGA', 'O_SPOTUP_FGMX'],
            'defensive': [],
        },
        'Transition': {
            'offensive': ['O_TRANS_PERCENTILE', 'O_TRANS_POSS_PCT', 'O_TRANS_PPP', 'O_TRANS_FG_PCT', 'O_TRANS_FT_POSS_PCT', 'O_TRANS_TOV_POSS_PCT', 'O_TRANS_SF_POSS_PCT', 'O_TRANS_PLUSONE_POSS_PCT', 'O_TRANS_SCORE_POSS_PCT', 'O_TRANS_EFG_PCT', 'O_TRANS_POSS', 'O_TRANS_PTS', 'O_TRANS_FGM', 'O_TRANS_FGA', 'O_TRANS_FGMX'],
            'defensive': [],
        },
    },
    'Shooting': {
        '5ft Range': {
            'offensive': ['O_FGM_LT_05', 'O_FGA_LT_05', 'O_FG_PCT_LT_05', 'O_FGM_LT_10_GT_05', 'O_FGA_LT_10_GT_05', 'O_FG_PCT_LT_10_GT_05', 'O_FGM_LT_15_GT_10', 'O_FGA_LT_15_GT_10', 'O_FG_PCT_LT_15_GT_10', 'O_FGM_LT_20_GT_15', 'O_FGA_LT_20_GT_15', 'O_FG_PCT_LT_20_GT_15', 'O_FGM_LT_25_GT_20', 'O_FGA_LT_25_GT_20', 'O_FG_PCT_LT_25_GT_20', 'O_FGM_LT_30_GT_25', 'O_FGA_LT_30_GT_25', 'O_FG_PCT_LT_30_GT_25', 'O_FGM_LT_35_GT_30', 'O_FGA_LT_35_GT_30', 'O_FG_PCT_LT_35_GT_30', 'O_FGM_LT_40_GT_35', 'O_FGA_LT_40_GT_35', 'O_FG_PCT_LT_40_GT_35', 'O_FGM_GT_40', 'O_FGA_GT_40', 'O_FG_PCT_GT_40'],
            'defensive': [],
        },
        '8ft Range': {
            'offensive': ['O_FGM_LT_08', 'O_FGA_LT_08', 'O_FG_PCT_LT_08', 'O_FGM_LT_16_GT_08', 'O_FGA_LT_16_GT_08', 'O_FG_PCT_LT_16_GT_08', 'O_FGM_LT_24_GT_16', 'O_FGA_LT_24_GT_16', 'O_FG_PCT_LT_24_GT_16', 'O_FGM_GT_24', 'O_FGA_GT_24', 'O_FG_PCT_GT_24'],
            'defensive': [],
        },
        'By Zone': {
            'offensive': ['O_FGM_RA', 'O_FGA_RA', 'O_FG_PCT_RA', 'O_FGM_PAINT_NRA', 'O_FGA_PAINT_NRA', 'O_FG_PCT_PAINT_NRA', 'O_FGM_MR', 'O_FGA_MR', 'O_FG_PCT_MR', 'O_FGM_LC3', 'O_FGA_LC3', 'O_FG_PCT_LC3', 'O_FGM_RC3', 'O_FGA_RC3', 'O_FG_PCT_RC3', 'O_FGM_AB3', 'O_FGA_AB3', 'O_FG_PCT_AB3', 'O_FGM_BC', 'O_FGA_BC', 'O_FG_PCT_BC', 'O_FGM_C3', 'O_FGA_C3', 'O_FG_PCT_C3'],
            'defensive': [],
        },
    },
    'Tracking': {
        'CatchShoot': ['CATCH_SHOOT_FGM', 'CATCH_SHOOT_FGA', 'CATCH_SHOOT_FG_PCT', 'CATCH_SHOOT_PTS', 'CATCH_SHOOT_FG3M', 'CATCH_SHOOT_FG3A', 'CATCH_SHOOT_FG3_PCT', 'CATCH_SHOOT_EFG_PCT'],
        'Defense': [],
        'Drives': ['DRIVES', 'DRIVE_FGM', 'DRIVE_FGA', 'DRIVE_FG_PCT', 'DRIVE_FTM', 'DRIVE_FTA', 'DRIVE_FT_PCT', 'DRIVE_PTS', 'DRIVE_PTS_PCT', 'DRIVE_PASSES', 'DRIVE_PASSES_PCT', 'DRIVE_AST', 'DRIVE_AST_PCT', 'DRIVE_TOV', 'DRIVE_TOV_PCT', 'DRIVE_PF', 'DRIVE_PF_PCT'],
        'Efficiency': [],
        'ElbowTouch': ['ELBOW_TOUCHES', 'ELBOW_TOUCH_FGM', 'ELBOW_TOUCH_FGA', 'ELBOW_TOUCH_FG_PCT', 'ELBOW_TOUCH_FTM', 'ELBOW_TOUCH_FTA', 'ELBOW_TOUCH_FT_PCT', 'ELBOW_TOUCH_PTS', 'ELBOW_TOUCH_PASSES', 'ELBOW_TOUCH_AST', 'ELBOW_TOUCH_AST_PCT', 'ELBOW_TOUCH_TOV', 'ELBOW_TOUCH_TOV_PCT', 'ELBOW_TOUCH_FOULS', 'ELBOW_TOUCH_PASSES_PCT', 'ELBOW_TOUCH_FOULS_PCT', 'ELBOW_TOUCH_PTS_PCT'],
        'PaintTouch': ['PAINT_TOUCHES', 'PAINT_TOUCH_FGM', 'PAINT_TOUCH_FGA', 'PAINT_TOUCH_FG_PCT', 'PAINT_TOUCH_FTM', 'PAINT_TOUCH_FTA', 'PAINT_TOUCH_FT_PCT', 'PAINT_TOUCH_PTS', 'PAINT_TOUCH_PTS_PCT', 'PAINT_TOUCH_PASSES', 'PAINT_TOUCH_PASSES_PCT', 'PAINT_TOUCH_AST', 'PAINT_TOUCH_AST_PCT', 'PAINT_TOUCH_TOV', 'PAINT_TOUCH_TOV_PCT', 'PAINT_TOUCH_FOULS', 'PAINT_TOUCH_FOULS_PCT'],
        'Passing': ['PASSES_MADE', 'PASSES_RECEIVED', 'FT_AST', 'SECONDARY_AST', 'POTENTIAL_AST', 'AST_PTS_CREATED', 'AST_ADJ', 'AST_TO_PASS_PCT', 'AST_TO_PASS_PCT_ADJ'],
        'Possessions': ['TOUCHES', 'FRONT_CT_TOUCHES', 'TIME_OF_POSS', 'AVG_SEC_PER_TOUCH', 'AVG_DRIB_PER_TOUCH', 'PTS_PER_TOUCH'],
        'PostTouch': ['POST_TOUCHES', 'POST_TOUCH_FGM', 'POST_TOUCH_FGA', 'POST_TOUCH_FG_PCT', 'POST_TOUCH_FTM', 'POST_TOUCH_FTA', 'POST_TOUCH_FT_PCT', 'POST_TOUCH_PTS', 'POST_TOUCH_PTS_PCT', 'POST_TOUCH_PASSES', 'POST_TOUCH_PASSES_PCT', 'POST_TOUCH_AST', 'POST_TOUCH_AST_PCT', 'POST_TOUCH_TOV', 'POST_TOUCH_TOV_PCT', 'POST_TOUCH_FOULS', 'POST_TOUCH_FOULS_PCT'],
        'PullUpShot': ['PULL_UP_FGM', 'PULL_UP_FGA', 'PULL_UP_FG_PCT', 'PULL_UP_PTS', 'PULL_UP_FG3M', 'PULL_UP_FG3A', 'PULL_UP_FG3_PCT', 'PULL_UP_EFG_PCT'],
        'Rebounding': ['OREB_CONTEST', 'OREB_UNCONTEST', 'OREB_CONTEST_PCT', 'OREB_CHANCES', 'OREB_CHANCE_PCT', 'OREB_CHANCE_DEFER', 'OREB_CHANCE_PCT_ADJ', 'AVG_OREB_DIST'],
        'SpeedDistance': ['DIST_MILES_O', 'AVG_SPEED_O'],
    },
}


# Standardize columns of a data frame
def standardize_columns(data, excluded_columns):
    # Temporarily remove excluded columns, so they are not altered
    excluded_columns_data = data[excluded_columns]
    data_to_standardize = data.drop(columns=excluded_columns)

    # Standardize all columns except excluded columns
    scaler = StandardScaler()
    standardized_data = pd.DataFrame(scaler.fit_transform(data_to_standardize), columns=data_to_standardize.columns,
                                     index=data_to_standardize.index)

    # Combine the excluded columns back with the standardized columns
    data = pd.concat([excluded_columns_data, standardized_data], axis=1)

    return data


# Load a single seasons stats
def load_single_season_stats(season, season_type, stats_filename, min_gp, min_mpg):
    # Get stats for the season
    stats = pd.read_csv(stats_filename.format(season, season_type))

    # Fill missing cells with 0s. Assuming that missing data means a player did not record a single stat for the column
    stats = stats.fillna(0)

    # Remove small sample sizes
    stats = stats[(stats['GP'] >= min_gp) | ((stats['MIN'] / stats['GP']) >= min_mpg)]

    # Standardize all columns except PLAYER_ID
    stats = standardize_columns(stats, ['PLAYER_ID'])

    return stats


# Combine multiple seasons of stats
def combine_seasons(seasons, season_types, stats_filename, min_gp, min_mpg):
    # Combine stats for each season
    combined = []
    for i, season in enumerate(seasons):
        for j, season_type in enumerate(season_types):
            # Get stats for this season
            stats = load_single_season_stats(season, season_type, stats_filename, min_gp, min_mpg)
            stats['SEASON'] = season
            stats['SEASON_TYPE'] = season_type

            # Add standardized stats to list of stats for every season
            combined.append(stats)

    # Concatenate dataframes for all seasons
    combined_df = pd.concat(combined)

    return combined_df


# Get input available input features based on the season
def get_input_features(season):
    # Get availability of stats
    availability = get_availability(season)
    stat_types = list(availability.keys())

    # Adjust all stats together for this season
    features = []
    for stat_type in stat_types:
        if availability[stat_type]:
            # Get box outs and hustle stats
            if stat_type == 'Box Outs' or stat_type == 'Hustle':
                features.extend(manual_inputs_map[stat_type])

            # Get defensive stats
            elif stat_type == 'Defense':
                for defense_category in defense_categories:
                    features.extend(manual_inputs_map[stat_type][defense_category])

            # Get general stats
            elif stat_type == 'General':
                for general_measure_type in general_measure_types:
                    features.extend(manual_inputs_map[stat_type][general_measure_type])

            # Get play type stats
            elif stat_type == 'Play Types':
                for play_type, defense in zip(play_types, play_type_defenses):
                    features.extend(manual_inputs_map[stat_type][play_type]['offensive'])
                    if defense:
                        features.extend(manual_inputs_map[stat_type][play_type]['defensive'])

            # Get shooting stats
            elif stat_type == 'Shooting':
                for distance_range in distance_ranges:
                    features.extend(manual_inputs_map[stat_type][distance_range]['offensive'])

                    features.extend(manual_inputs_map[stat_type][distance_range]['defensive'])

            # Get tracking stats
            elif stat_type == 'Tracking':
                for track_type in track_types:
                    features.extend(manual_inputs_map[stat_type][track_type])

    return features


# Use a Pearson correlation matrix to find redundancies between columns
def find_redundant_columns_pearson(data, threshold, already_chosen=None, one_by_one=False,
                                   features_filename='features.pkl'):
    # Get correlation matrix for data
    corr_matrix = data.corr()

    # Get the original set of features
    chosen_features = list(corr_matrix.columns)
    if already_chosen is not None:
        chosen_features = already_chosen

    # Loop over the correlation matrix
    for i in range(len(corr_matrix.columns)):
        for j in range(i + 1, len(corr_matrix.columns)):
            # If the correlation between these columns meets the threshold, handle it
            if abs(corr_matrix.iloc[i, j]) >= threshold:
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]

                # If both columns are still in the chosen features, print them
                if col1 in chosen_features and col2 in chosen_features:
                    correlation_value = corr_matrix.iloc[i, j]
                    print(f"Correlation between {col1} and {col2}: {correlation_value:.2f}")

                    # Prompt for removal of a column
                    if one_by_one:
                        remove = input(f'Remove [1/2/x]?: ')
                        if remove == '1':
                            chosen_features.remove(col1)
                        elif remove == '2':
                            chosen_features.remove(col2)

    # Save chosen columns to file
    if one_by_one:
        with open(features_filename, 'wb') as fp:
            pickle.dump(chosen_features, fp)


# Use variance inflation factors to find redundancies between columns
def find_redundant_columns_vif(data, threshold, already_chosen=None, one_by_one=False,
                               features_filename='features.pkl'):
    # Add intercept to the model
    vif_model = sm.add_constant(data)

    # Compute VIF for each predictor
    vif_data = pd.DataFrame()
    vif_data['Feature'] = vif_model.columns
    vif_data['VIF'] = [variance_inflation_factor(vif_model.values, i) for i in range(vif_model.shape[1])]

    # Get the original set of features
    chosen_features = list(data.columns)
    if already_chosen is not None:
        chosen_features = already_chosen

    # Loop over VIF for each predictor
    for _, (feature, vif) in vif_data.iterrows():
        # If the VIF for this column is above the threshold, handle it
        if vif >= threshold and feature in chosen_features:
            print(f"VIF for {feature}: {vif:.2f}")

            # Prompt for removal of a column
            if one_by_one:
                remove = input(f'Remove [y/n]?: ')
                if remove == 'y':
                    chosen_features.remove(feature)

    # Save chosen columns to file
    if one_by_one:
        with open(features_filename, 'wb') as fp:
            pickle.dump(chosen_features, fp)


# Get available chosen columns
def get_available_chosen_columns(season, chosen_inputs):
    # Get manual input features available
    manual_inputs = get_input_features(season)

    # Only use chosen features if they are available
    input_features = []
    for input_feature in chosen_inputs:
        if input_feature in manual_inputs:
            input_features.append(input_feature)

    return input_features


if __name__ == '__main__':
    seasons = range(1996, 2024)
    seasons = [f'{season}-{((season % 100) + 1) % 100:02}' for season in seasons]
    season_types = ['Regular Season', 'Playoffs']
    save_filename = '../Data/SeasonStats/Combined/RateAdjusted/{}_{}.csv'

    # Get combined stats for every season
    stats = combine_seasons(seasons, season_types, save_filename, 10, 12)
    stats.to_csv('../Data/SeasonStats/Combined/all_seasons_standardized.csv', index=False)

    # Find redundant columns
    # manual_inputs = get_input_features(seasons[0])
    # stats = stats[manual_inputs]
    # find_redundant_columns_pearson(stats, 0.8, one_by_one=True, features_filename=f'chosen_features.pkl')
    # find_redundant_columns_vif(stats, 10, one_by_one=True, features_filename=f'chosen_features.pkl')

    # Load features chosen
    # with open('chosen_features.pkl', 'rb') as fp:
    #     chosen_inputs = pickle.load(fp)
    #
    #     # Only use chosen features if they are available
    #     input_features = get_available_chosen_columns(seasons[0], chosen_inputs)
    #     print(len(input_features))
