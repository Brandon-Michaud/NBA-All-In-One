import numpy as np
import pandas as pd
from sklearn.model_selection import KFold


# Split a dataframe into folds
def create_folds(df, n_folds, seed=42):
    # Create fold splitter object
    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)

    # Create a new column for fold labels
    df['FOLD'] = -1

    # Assign fold numbers to each row
    for fold, (train_index, test_index) in enumerate(kf.split(df)):
        df.loc[test_index, 'FOLD'] = fold

    return df


# Get training and testing splits based on rotation
def get_splits_for_rotation(df, n_training, n_testing, rotation):
    # Get fold numbers corresponding to splits
    training_fold_numbers = [((i + rotation) % (n_training + n_testing)) for i in range(n_training)]
    testing_fold_numbers = [((i + rotation + n_training) % (n_training + n_testing)) for i in range(n_testing)]

    # Get data corresponding to splits
    training_df = df[df['FOLD'].isin(training_fold_numbers)]
    testing_df = df[df['FOLD'].isin(testing_fold_numbers)]

    return training_df, testing_df


if __name__ == '__main__':
    data = {
        'Column1': np.random.randint(0, 100, 50),
        'Column2': np.random.random(50),
        'Column3': np.random.choice(['A', 'B', 'C', 'D'], 50)
    }
    sample = pd.DataFrame(data)
    sample_with_folds = create_folds(sample, 10)
    sample_train, sample_test = get_splits_for_rotation(sample_with_folds, 9, 1, 0)
    print(sample_test)
