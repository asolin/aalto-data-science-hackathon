import numpy as np
import pandas as pd
from sklearn.decomposition import ProjectedGradientNMF


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

    print(np.shape(mu))

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



def save_pca_maps_to_json(X, filename):

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
    

    
def analyse(filename, K, method='pca'):

    # Get data
    data = pd.read_csv(filename)
    X = np.array(data)

    # Run PCA
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
