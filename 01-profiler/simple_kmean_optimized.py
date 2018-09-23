#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd


def load_and_process():
    result = pd.read_csv('./data/nba-player-2014.csv', na_values='-')
    result.fillna(0, inplace=True)
    return result


def filter_columns(dataframe, excluded):
    return dataframe[list(set(dataframe.columns) - set(excluded))]


def normalize(dataframe):
    return (dataframe - dataframe.mean()) / dataframe.std()


def calculate_distance(s1, s2):
    return np.sqrt(np.power(s1 - s2, 2).sum(axis=1))


def kmeans(stat, k, iterations):
    belongings = None
    centers = stat.sample(n=k)
    for i in range(iterations):
        centers.reset_index(drop=True, inplace=True)
        if i > 0 and i % 10 == 0:
            print('iteration round', i)
        distance_matrix = centers.apply(lambda c: calculate_distance(stat, c), axis=1)
        belongings = distance_matrix.idxmin()
        centers = stat.groupby(belongings).mean()
    return belongings


def main():
    distance_excluded_columns = ['fullname']
    players = load_and_process()
    normalized_stat = normalize(filter_columns(players, distance_excluded_columns))

    labels = kmeans(normalized_stat, 5, 100)

    players.groupby(labels).count().max(axis=1)

    players['Group'] = labels

    james = players[players.fullname == 'James, LeBron']
    james_group = players.Group == james.Group.iloc[0]

    distances = calculate_distance(normalized_stat[james_group], normalized_stat.loc[james.index].iloc[0])
    distances.name = 'Distance'
    pd.concat([players[james_group], distances], axis=1).sort_values(by='Distance')


if __name__ == '__main__':
    main()