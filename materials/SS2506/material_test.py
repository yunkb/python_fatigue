import pickle
from subprocess import Popen

import matplotlib.pyplot as plt
import matplotlib

from stress_strain_evaluation import SS2506
from stress_strain_evaluation import experiments

matplotlib.style.use('classic')
plt.rc('text', usetex=True)
plt.rc('font', serif='Computer Modern Roman')
plt.rcParams.update({'font.size': 20})
plt.rcParams['text.latex.preamble'] = [r"\usepackage{amsmath}"]
plt.rc('font', **{'family': 'serif', 'serif': ['Computer Modern Roman'],
                  'monospace': ['Computer Modern Typewriter']})


class MaterialTest:
    def __init__(self, strain, hardness, austenite):
        self.strain = strain
        self.hardness = hardness
        self.austenite = austenite
        self.name = 'material_test_hv=' + str(hardness) + '_au=' + str(austenite).replace('.', '_')

    def _write_input_file(self):
        SS2506.write_material_input_file('SS2506material.inc')
        file_lines = ['**',
                      '**',
                      '** Autogenerated input file created by Case Hardening Simulation Toolbox, version 0.8.1',
                      '** Written by Niklas Melin and Erik Olsson',
                      '**',
                      '*Heading',
                      '\t Case Hardening Simulation Toolbox - Thermal - Niklas Melin 2012',
                      '*Preprint, echo=NO, model=NO, history=NO, contact=NO',
                      '**',
                      '** ----------------------------------------------------------------',
                      '** Load required include files',
                      '**',
                      '**   Create Geometry',
                      '*Node, nset=all_nodes',
                      '\t1, \t 0., 0., 0.',
                      '\t2, \t 1., 0., 0.',
                      '\t3, \t 1., 1., 0.',
                      '\t4, \t 0., 1., 0.',
                      '\t5, \t 0., 0., 1.',
                      '\t6, \t 1., 0., 1.',
                      '\t7, \t 1., 1., 1.',
                      '\t8, \t 0., 1., 1.',
                      '*Element, type=C3D8, elset=all_elements',
                      '\t1, 1, 2, 3, 4, 5, 6, 7, 8',
                      '**',
                      '** ----------------------------------------------------------------',
                      '**',
                      '**   Define material properties',
                      '**',
                      '*Solid Section, elset=all_elements, material=SS2506',
                      '*Material, name=SS2506',
                      '\t*Include, Input=SS2506material.inc',
                      '*INITIAL CONDITIONS, TYPE=FIELD, VAR=1',
                      '\tALL_NODES , ' + str(self.hardness),
                      '**',
                      '*INITIAL CONDITIONS, TYPE=FIELD, VAR=2',
                      '\tALL_NODES , ' + str(self.austenite),
                      '*Boundary',
                      '**',
                      '\t1, 1, 3',
                      '\t2, 2, 3',
                      '\t3, 3, 3',
                      '\t4, 1, 1',
                      '\t4, 3, 3',
                      '\t5, 1, 2',
                      '\t6, 2, 2',
                      '\t8, 1, 1',
                      '**',
                      '*STEP, NAME=material_test , INC=10000, Amplitude=Ramp',
                      '\t Material test of one element',
                      '\t*STATIC',
                      '\t\t0.01, 1.0, 1e-05, 1.0',
                      '\t*Boundary',
                      '\t\t5, 3, 3, ' + str(self.strain),
                      '\t\t6, 3, 3, ' + str(self.strain),
                      '\t\t7, 3, 3, ' + str(self.strain),
                      '\t\t8, 3, 3, ' + str(self.strain),
                      '\t*OUTPUT, FIELD, FREQ=1',
                      '\t\t*ELEMENT OUTPUT, directions=YES',
                      '\t\t\tS, E, FV',
                      '*END STEP']

        with open(self.name + '.inp', 'w') as inp_file:
            for line in file_lines:
                inp_file.write(line + '\n')
            inp_file.write('**EOF')

    @staticmethod
    def _write_env_file():
        file_lines = ['ask_delete = OFF']

        with open('abaqus_v6.env', 'w') as env_file:
            for line in file_lines:
                env_file.write(line + '\n')

    def run_material_test(self):
        self._write_input_file()
        self._write_env_file()
        abq = '/scratch/users/erik/SIMULIA/CAE/2018/linux_a64/code/bin/ABQLauncher'
        process = Popen(abq + ' j=' + self.name + ' interactive ', shell=True)
        process.wait()
        process = Popen(abq + ' python material_test_post_processing.py ' + self.name, shell=True)
        process.wait()

        with open('data_' + self.name + '.pkl', 'r') as pickle_handle:
            data = pickle.load(pickle_handle)
        return data


if __name__ == '__main__':
    for experiment in experiments:
        plt.figure(0)
        experiment.plot()

        test = MaterialTest(experiment.strain[-1], experiment.hardness, experiment.ra/100)
        stress_data = test.run_material_test()
        plt.plot(stress_data[:, 3], stress_data[:, 9], '--' + experiment.color, lw=2)
    plt.show()
