import numpy as np

import pickle
import matplotlib.pyplot as plt

case_depths = [0.8]
color = ['r', 'b', 'g', 'k']


def martensite(carbon):
    def poly(x):
        return -2.07934384e+04*x**2 + 2.98225944e+02*x - 1.60574051e-01
    if np.isscalar(carbon):
        carbon = np.array([carbon])
    q = poly(carbon)
    q[carbon < 0.0022] = poly(0.0022)
    return q

for case_depth, c in zip(case_depths, color):
    with open('../pickles/tooth_root_data/data' + str(case_depth).replace('.', '_') + '.pkl') as pickle_handle:
        flank_data = pickle.load(pickle_handle)
        root_data = pickle.load(pickle_handle)
    plt.figure(0)
    plt.plot(flank_data[:, 1], flank_data[:, 4], c, lw=2)
    plt.plot(root_data[:, 1], root_data[:, 4], '--' + c, lw=2)

    x = root_data[root_data[:, 1] > 0.0023, 1]
    y = root_data[root_data[:, 1] > 0.0023, 4]
    print np.polyfit(x, y, 2)

    x = np.linspace(0.002, 0.01, 1000)
    plt.plot(x, martensite(x))

    plt.figure(1)
    plt.plot(flank_data[:, 1], flank_data[:, 2], c, lw=2)
    plt.plot(root_data[:, 1], root_data[:, 2], '--' + c, lw=2)

plt.show()