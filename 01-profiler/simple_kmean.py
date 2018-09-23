import math

import pandas as pd


def load_and_process():
    result = pd.read_csv('./data/nba-player-2014.csv', na_values='-')
    result.fillna(0, inplace=True)
    return result


def euclidean_distance(row1, row2):
    """
    A simple euclidean distance function
    """
    inner_value = 0
    # different from KNN in which two sub data frames were received, here two series are passed into this function
    for k in row1.index:
        inner_value += (row1[k] - row2[k]) ** 2
    return math.sqrt(inner_value)


def filter_columns(dataframe, excluded):
    return dataframe[list(set(dataframe.columns) - set(excluded))]


def normalize(dataframe):
    return (dataframe - dataframe.mean()) / dataframe.std()


def insert_to_group(row, centers, groups):
    distances = pd.DataFrame({
        'dist': centers.apply(lambda r: euclidean_distance(r, row), axis='columns'),
    })
    distances.reindex()
    distances.sort_values(by='dist', inplace=True)
    groups[distances.index[0]] = groups[distances.index[0]].append(row)


def test_kmean(k, iterations, normalize_stat=True):
    groups = []
    distance_excluded_columns = ['fullname']
    players = load_and_process()
    if normalize_stat:
        stat = normalize(filter_columns(players, distance_excluded_columns))
    else:
        stat = filter_columns(players, distance_excluded_columns)

    centers = stat.sample(n=k)
    centers.reset_index(drop=True, inplace=True)

    for i in range(iterations):
        if i > 0 and i % 10 == 0:
            print('iteration round', i)
        groups = []
        for _ in range(k):
            groups.append(pd.DataFrame())

        stat.apply(lambda r: insert_to_group(r, centers, groups), axis='columns')

        # update centers
        centers = pd.DataFrame(
            list(map(lambda g: g.mean(), groups))
        )
    return list(map(lambda g: players[players.index.isin(g.index)], groups)), centers


def main():
    groups, centers = test_kmean(5, 100)
    for idx, g in enumerate(groups):
        # print('centers:')
        # print(centers.iloc[idx])
        print('group %d has %d members:' % (idx, groups[idx].shape[0]))
        print('members:')
        print(groups[idx].head())


if __name__ == '__main__':
    main()
