from sklearn import preprocessing
import numpy as np


def Normalization(x):
    """
    线性归一化，映射到[-1,1]
    """
    return [(float(i) - np.mean(x)) / float(max(x) - min(x)) for i in x]


def normalization(x):
    """
    调包进行线性归一化，映射到[0,1]
    """
    X = np.array(x)
    scaler = preprocessing.MinMaxScaler()
    return scaler.fit_transform(X)


def Standard_normalization(x):
    """
    标准差标准化
    """
    X = np.array(x)
    # calculate mean
    X_mean = X.mean(axis=0)
    # calculate variance
    X_std = X.std(axis=0)
    print('均值：', X_mean)
    print('方差：', X_std)
    return (X-X_mean)/X_std


def standard_normalization(X):
    """
    调包进行标准差标准化，按属性（列）进行，求每列的均值、方差
    """
    return preprocessing.scale(np.array(X))

def zero_one_normalization(X):
    """
        二值化
    """
    binarizer = preprocessing.Binarizer().fit(X)
    print(binarizer.transform(X))


def sigmoid(X, useStatus):
    if useStatus:
        return 1.0 / (1 + np.exp(-float(X)))
    else:
        return float(X)



if __name__ == '__main__':

    # X = np.array([[1., -1., 2.],
    #               [2., 0., 0.],
    #               [0., 1., -1.]])
    # X_mean = X.mean(axis=0)
    # X_std = X.std(axis=0)
    # # print(X_mean)
    # # print(X_std)
    #
    #
    #
    # X_normalized = preprocessing.normalize(X, norm='l2')
    #
    # print(X_normalized)
    #
    #
    # x = np.array([3, 0, -4])
    # n2 = np.linalg.norm(x, ord=2)
    # print(n2)


    # x = np.array([[-1, 1, 0], [-4, 3, 0], [1, 0, 2]])
    # print(x)
    #
    # xtx = np.matmul(x.T, x)  # 矩阵的转置*矩阵
    # print("lambda  ", np.linalg.eigvals(xtx))  # 特征值
    #
    # n2 = np.linalg.norm(x, ord=2)
    # print('norm_2  ', n2, np.sqrt(27.71086452))
    print(int(""))


