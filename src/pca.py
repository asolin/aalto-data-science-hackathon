
# Copyright (c) 2015 Jaakko Luttinen
# GPL v3

import numpy as np
import pandas as pd
from sklearn.decomposition import ProjectedGradientNMF
import matplotlib.pyplot as plt

def _nmf(X, K):
    nmf = ProjectedGradientNMF(n_components=K, max_iter=1000)
    nmf.fit(X)

    B = nmf.components_
    A = np.dot(X, np.linalg.pinv(B))

    return (A, B)
    

def _pca(X, K, center=None):

    if center is not None:
        mu = np.mean(X, axis=center, keepdims=True)
        X = X - mu
    else:
        mu = 0

    (M, N) = np.shape(X)

    A = np.random.randn(M, K)
    B = np.random.randn(K, N)

    for i in range(100):
        B = np.linalg.solve(np.dot(A.T, A), np.dot(A.T, X))
        A = np.linalg.solve(np.dot(B, B.T), np.dot(B, X.T)).T

    #
    # Find rotation
    #

    # Whiten B
    (U_B, s_B, V_B) = np.linalg.svd(B, full_matrices=False)
    B = V_B

    # Orthogonalize A
    A = np.dot(A, U_B * s_B)
    (U_A, s_A, V_A) = np.linalg.svd(A, full_matrices=False)
    A = U_A * s_A
    B = np.dot(V_A, B)

    return (A, B, mu)



def save_maps_to_json(X, filename):

    f = open(filename, 'w')

    f.write('{"stops": [')
    for i in range(len(X)):
        f.write('{')
        f.write('"id": {0}, "coords": [{1}, {2}], "value": ['.format(X.iloc[i].name,
                                                                     X.iloc[i].coords[0],
                                                                     X.iloc[i].coords[1]))
        for j in range(len(X.iloc[i].values)-2):
            f.write('{0}, '.format(X.iloc[i][j]))
        f.write('{0}]'.format(X.iloc[i][j+1]))
        f.write('}')
        if i < len(X)-1:
            f.write(', ')
    f.write(']}')
    return


def save_routes_to_json(X, filename):

    # Discard small values to reduce the number of routes
    X = X[np.any(np.abs(X)>0.05, axis=1)]
    
    f = open(filename, 'w')

    f.write('[')
    for i in range(len(X)):
        f.write('{')
        (from_stop, to_stop) = X.index[i].split('-')
        from_stop = int(from_stop)
        to_stop = int(to_stop)
        f.write('"id": [{0}, {1}], "value": ['.format(to_stop,
                                                      from_stop))
        j = -1
        for j in range(len(X.iloc[i].values)-2):
            f.write('{0}, '.format(X.iloc[i][j]))
        f.write('{0}]'.format(X.iloc[i][j+1]))
        f.write('}')
        if i < len(X)-1:
            f.write(', ')
    f.write(']')
    return


def analyse_stops(filename, K, method='nmf'):

    # Get data
    data = pd.read_csv(filename)
    X = np.array(data)

    # Run PCA/NMF
    if method == 'pca':
        (A, B, mu) = _pca(X, K, center=0)
    elif method == 'nmf':
        (A, B) = _nmf(X, K)

    # Label PCA map elements with bus stop IDs
    B = pd.DataFrame(B, columns=data.columns).T
    B.index = B.index.astype(int)

    # Combine bus stop information to PCA maps
    stops = pd.read_json("../site/stops.json")
    coords = [stops.iloc[i].iloc[0]['coords'] for i in range(len(stops))]
    iden = [stops.iloc[i].iloc[0]['id'] for i in range(len(stops))]
    busstops = pd.DataFrame(
        columns=["coords"],
        index=iden,
        data={
            "coords": coords,
             }
    )
    pca_maps = pd.merge(busstops, B, left_index=True, right_index=True, how='inner')

    # Label PCA time series elements
    pca_timeseries = pd.DataFrame(A)

    return (pca_maps, pca_timeseries)


def analyse_routes(filename, K, method='pca'):

    # Get data
    data = pd.read_csv(filename)
    X = np.array(data)

    # Run PCA/NMF
    if method == 'pca':
        (A, B, mu) = _pca(X, K, center=0)
    elif method == 'nmf':
        (A, B) = _nmf(X, K)

    # Label PCA map elements with bus stop IDs
    B = pd.DataFrame(B, columns=data.columns).T
    #B.index = B.index.astype(int)

    if False:

        # Combine bus stop information to PCA maps
        stops = pd.read_json("../site/stops.json")
        coords = [stops.iloc[i].iloc[0]['coords'] for i in range(len(stops))]
        iden = [stops.iloc[i].iloc[0]['id'] for i in range(len(stops))]
        busstops = pd.DataFrame(
            columns=["coords"],
            index=iden,
            data={
                "coords": coords,
                 }
        )
        pca_routes = pd.merge(busstops, B, left_index=True, right_index=True, how='inner')
    else:
        pca_routes = B

    # Scale values to [-1, 1]
    pca_routes = pca_routes / np.max(np.abs(pca_routes))
    if method == 'pca':
        mu = pd.DataFrame(mu/np.max(np.abs(mu)), columns=data.columns).T

    # Label PCA time series elements
    pca_timeseries = pd.DataFrame(A)

    if method == 'pca':
        return (mu, pca_routes, pca_timeseries)
    else:
        return (pca_routes, pca_timeseries)


def plot_ts(X):
    if X.columns[0] == 'coords':
        N = len(X.columns) - 1
    else:
        N = len(X.columns)

    plt.figure()
    for i in range(N):
        plt.subplot(N, 1, i+1)
        plt.plot(X[i], 'k-')
        plt.yticks([0])
        plt.xticks([0, 0.5*24,
                    1*24, 1.5*24,
                    2*24, 2.5*24,
                    3*24, 3.5*24,
                    4*24, 4.5*24,
                    5*24, 5.5*24,
                    6*24, 6.5*24],
                   ['Sun', '12:00',
                    'Mon', '12:00',
                    'Tue', '12:00',
                    'Wed', '12:00',
                    'Thu', '12:00',
                    'Fri', '12:00',
                    'Sat', '12:00'])
        plt.xlim([0, 7*24-1])


def save_plot_ts(X, base_filename):
    if X.columns[0] == 'coords':
        N = len(X.columns) - 1
    else:
        N = len(X.columns)

    fig = plt.figure(figsize=(15, 1.5))
    for i in range(N):
        fig.clf()
        plt.plot(X[i], 'k-', linewidth=3)
        plt.yticks([0])
        plt.xticks([0, 0.5*24,
                    1*24, 1.5*24,
                    2*24, 2.5*24,
                    3*24, 3.5*24,
                    4*24, 4.5*24,
                    5*24, 5.5*24,
                    6*24, 6.5*24],
                   ['Sun', '12:00',
                    'Mon', '12:00',
                    'Tue', '12:00',
                    'Wed', '12:00',
                    'Thu', '12:00',
                    'Fri', '12:00',
                    'Sat', '12:00'])
        plt.xlim([0, 7*24-1])
        ax = plt.gca()
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        plt.savefig(base_filename + str(i) + ".png", bbox_inches='tight', transparent=True, dpi=300)
