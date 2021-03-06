from __future__ import print_function

from collections import namedtuple
import numpy as np

SteelData = namedtuple('Steel_data', ['HV'])
PhaseData = namedtuple('PhaseData', ['Martensite', 'Austenite', 'Bainite', 'Pearlite', 'Ferrite'])


class SS2506MaterialTemplate:
    def __init__(self, swa, swb, mb):
        self.ne = np.log(1e5)
        self.ns = np.log(0.1)
        self.b = 5.
        self.sw_par = [swa, swb]
        self.m_par = [mb]

        self.name = 'SS2506'

        self.transformation_strain = PhaseData(Martensite=self._trans_strain_martensite,
                                               Austenite=self._trans_strain_austenite,
                                               Bainite=self._trans_strain_bainite,
                                               Pearlite=self._trans_strain_fp,
                                               Ferrite=self._trans_strain_fp)

        self.thermal_expansion = PhaseData(Martensite=self._thermal_exp_martensite,
                                           Austenite=self._thermal_exp_austenite,
                                           Bainite=self._thermal_exp_bainite,
                                           Pearlite=self._thermal_exp_fp,
                                           Ferrite=self._thermal_exp_fp)

        self.composition = {'C': 0.221, 'Si': 0.24, 'Mn': 0.90, 'P': 0.007, 'S': 0.042, 'Cr':  0.56, 'Ni': 0.44,
                            'Mo': 0.18, 'Cu': 0.14, 'Al': 0.028}

    @staticmethod
    def findley_k(steel_properties):
        return -1.37143 + 0.0037143*steel_properties.HV

    def weibull_sw(self, steel_properties):
        return self.sw_par[0] + self.sw_par[1]*steel_properties.HV

    def weibull_m(self, steel_properties):
        return self.m_par[0]/steel_properties.HV**2

    # Phase transformation data
    def _trans_strain_martensite(self, temperature, carbon):
        t, c = np.meshgrid(temperature, carbon)
        e = -3.15814370e-03 + 1.2e-05*t + 2.9e-09*t**2 + 8.19710239e-03*c*100 - 1.67270626e-04*(c*100)**2
        return np.squeeze(e)

    @staticmethod
    def _thermal_exp_martensite(temperature, carbon):
        temperature = temperature + 273.15
        t, _ = np.meshgrid(temperature, carbon)
        a = 1.01552103e-05 + 5.99517668e-09*temperature
        return np.squeeze(a)

    @staticmethod
    def _trans_strain_austenite(temperature, carbon):
        t, c = np.meshgrid(temperature, carbon)

        e = -1.14649419e-02 + t*2.37764264e-05 + 4.22083943e-01*c
        return np.squeeze(e)

    @staticmethod
    def _thermal_exp_austenite(temperature, carbon):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        a = 2.4e-5 + 0*t
        return np.squeeze(a)

    @staticmethod
    def _trans_strain_fp(temperature, carbon):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        e = 2.2520e-9*t**2 + 1.1643e-5*t - 3.6923e-3
        return np.squeeze(e)

    @staticmethod
    def _thermal_exp_fp(temperature, carbon):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        a = 2*2.2520e-9*t + 1.1643e-5
        return np.squeeze(a)

    @staticmethod
    def _trans_strain_bainite(temperature, carbon):
        t, c = np.meshgrid(temperature, carbon)
        e = 2.38388172e-04 + 1.02978980e-05*t + 7.62158599e-09*t**2 - 5.39839566e-04*c - 1.13198683e-03*c**2
        return np.squeeze(e)

    def _thermal_exp_bainite(self, temperature, carbon):
        a = self._thermal_exp_fp(temperature, carbon)
        return np.squeeze(a)

    @staticmethod
    def ms_temperature(carbon):
        return np.interp(carbon, [0.002, 0.005, 0.008], [383.4953141884797, 272.5661649983974, 164.870608528147])

    def martensite_fraction(self, temperature, carbon, austenite_fraction=None):
        temperature = temperature + 273.15
        t, c = np.meshgrid(temperature, carbon)
        if isinstance(carbon, float):
            carbon = np.array([carbon])
        martensite_start_temp = self.ms_temperature(carbon)
        # a = 4.8405e-2 - 4.3710*carbon
        a = 0.05344308817192316*np.exp(-144.08873331961297*carbon)
        f = 0 * t
        for i, ms in enumerate(martensite_start_temp):
            f[i, temperature < ms] = 1-np.exp(-a[i]*(ms-temperature[temperature < ms]))
        if austenite_fraction is None:
            austenite_fraction = 0*f + 1.
        return np.squeeze(f * austenite_fraction)


# SS2506 = SS2506MaterialTemplate(swa=138, swb=0.71, mb=11.06e6)
# SS2506 = SS2506MaterialTemplate(swa=378, swb=0.175, mb=6.15e6)
SS2506 = SS2506MaterialTemplate(swa=900, swb=0, mb=15.)

if __name__ == '__main__':
    # Testing the transformation functions
    # carb = np.linspace(0.002, 0.0012, 10)
    # temp = np.linspace(0, 1000, 100)
    carb = 0.004
    temp = 300

    for trans_strain_func in SS2506.transformation_strain:
        print(trans_strain_func, trans_strain_func(temp, carb))

    carb = np.linspace(0.002, 0.01, 10)
    temp = np.linspace(0, 1000, 100)
    SS2506.martensite_fraction(temp, carb)

    print(SS2506.transformation_strain.Martensite(0, 0))
