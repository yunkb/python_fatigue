from collections import namedtuple

import numpy as np

import matplotlib.pyplot as plt
import matplotlib

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


class Experiment:
    def __init__(self, filename, color, hardness, ra, delimiter=None, compression=False):
        self.color = color
        sign = 1
        if compression:
            sign = -1
        data = sign*np.genfromtxt(filename, delimiter=delimiter)
        self.strain = data[:, 0]
        self.stress = data[:, 1]
        self.E = 205e3
        self.hardness = hardness
        self.ra = ra

    def plot(self):
        plt.plot(self.strain, self.stress, self.color, lw=2)

    def plastic_strain_data(self, threshold=0.0001):
        epl = self.strain - self.stress/self.E
        s = self.stress[epl > threshold]
        return epl[epl > threshold], s


class SS2506Material:
    def __init__(self, stress_strain_datasets):
        self.E = 205e3
        self.plastic_data = np.zeros((1000, len(stress_strain_datasets)))

        self.dp_parameter = 2.15
        self.dp_ra = 0.2
        self.hardness_values = np.zeros(len(stress_strain_datasets))

        self.epl = np.linspace(0., 0.025, 1000)
        for i, dataset in enumerate(stress_strain_datasets):
            self.plastic_data[:, i] = np.interp(self.epl, dataset.plastic_strain_data()[0],
                                                dataset.plastic_strain_data()[1])
            self.hardness_values[i] = dataset.hardness

    def strain(self, stress, hardness, ra, compression=True):
        print self.plastic_data
        compressive_plastic_stress = (self.plastic_data[:, 0]
                                      + (self.plastic_data[:, 1] - self.plastic_data[:, 0])
                                      / (np.diff(self.hardness_values)) * (hardness - self.hardness_values[0]))

        if not compression:
            compressive_plastic_stress /= (1 + (self.dp_parameter - 1)*(ra/self.dp_ra))

        return stress/self.E + np.interp(stress, compressive_plastic_stress, self.epl)

    def write_material_input_file(self, filename):
        file_lines = ['*Elastic',
                      '\t' + str(self.E) + ', 0.3',
                      '*Drucker Prager, Shear Criterion=Linear, Dependencies=2',
                      '\t0., 1., 0., , 0., 0.',
                      '\t0., 1., 0., , 1000., 0.',
                      '\t47.6, 1., 0.009346, , 0., 0.2'
                      '\t47.6, 1., 0.009346, , 1000., 0.2',
                      '*Drucker Prager Hardening, Type=Compression, Dependencies=1']

        for i, epl_val in enumerate(self.epl):
            file_lines.append('\t' + str(epl_val) + ', ' + str(self.plastic_data[i, 0]) + ', ,'
                              + str(self.hardness_values[0]))
            file_lines.append('\t' + str(epl_val) + ', ' + str(self.plastic_data[i, 1]) + ', ,'
                              + str(self.hardness_values[1]))

        with open(filename, 'w') as material_file:
            for line in file_lines:
                material_file.write(line + '\n')
            material_file.write('**EOF')


experiments = [Experiment(filename='compression_data_case_EN.dat', color='b', delimiter=',', compression=True,
                          hardness=750, ra=20),
               Experiment(filename='tension_data_case_EN.dat', color='r', delimiter=',',
                          hardness=750, ra=20),
               Experiment(filename='tension_data_case_BA.dat', color='g',
                          hardness=750, ra=20),
               Experiment(filename='tension_data_core_BA.dat', color='k',
                          hardness=450, ra=0)]

SS2506 = SS2506Material((experiments[3], experiments[0]))

if __name__ == '__main__':
    for experiment in experiments:
        plt.figure(0)
        experiment.plot()

        e_pl, stress = experiment.plastic_strain_data()
        plt.figure(1)
        plt.plot(e_pl, stress, experiment.color, lw=2)

    s = np.linspace(0, 1000, 1000)
    plt.figure(0)
    plt.plot(SS2506.strain(s, 450, 0.6, compression=False), s)

    plt.show()
