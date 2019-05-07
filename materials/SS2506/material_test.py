from subprocess import Popen

from stress_strain_evaluation import SS2506


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

    def run_material_test(self):
        self._write_input_file()
        abq = '/scratch/users/erik/SIMULIA/CAE/2018/linux_a64/code/bin/ABQLauncher'
        process = Popen(abq + ' j=' + self.name + ' interactive ', shell=True)
        process.wait()


if __name__ == '__main__':
    test = MaterialTest(-0.025, 750, 0.2)
    test.run_material_test()
