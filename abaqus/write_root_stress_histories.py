from visualization import *
from abaqusConstants import *

import pickle
import numpy as np

from path_functions import create_path
from path_functions import get_stress_tensors_from_path

torque = 400
tooth_odb_file_name = '/scratch/users/erik/scania_gear_analysis/odb_files/planet_gear_stresses_' + str(torque) + \
                      '_Nm.odb'

with open('../planetary_gear/pickles/tooth_paths.pkl', 'rb') as path_pickle_handle:
    pickle.load(path_pickle_handle)                 # Flank path data
    pickle.load(path_pickle_handle)                 # Direction vector of the flank path
    root_data = pickle.load(path_pickle_handle)     # Root path data
    normal_root = pickle.load(path_pickle_handle)   # Direction vector perpendicular the root path


path_data_pos = np.zeros((100, 3))
path_data_pos[:, 0:3] = root_data
path_data_neg = np.copy(path_data_pos)

path_data_neg[:, 0] *= -1

normal_root_pos = normal_root
normal_root_neg = np.copy(normal_root_pos)
normal_root_neg[0] *= -1

odb = openOdb(tooth_odb_file_name, readOnly=True)
session.Viewport(name='Viewport: 1', origin=(0.0, 0.0), width=309.913116455078,
                 height=230.809509277344)
session.viewports['Viewport: 1'].makeCurrent()
session.viewports['Viewport: 1'].maximize()
o7 = session.odbs[session.odbs.keys()[0]]
session.viewports['Viewport: 1'].setValues(displayedObject=o7)
step_index = odb.steps.keys().index('mechanical_stresses')
frames = odb.steps['mechanical_stresses'].frames
number_of_frames = len(frames)
for root_path_data, name, normal_root in zip([path_data_pos, path_data_neg], ['pos', 'neg'],
                                             [normal_root_pos, normal_root_neg]):
    root_path = create_path(root_path_data, 'root_path_' + name, session)
    stress_data = np.zeros((number_of_frames, 2))
    for frame_idx in range(number_of_frames):
        session.viewports['Viewport: 1'].odbDisplay.setFrame(step=step_index, frame=frame_idx)
        stress_tensors = get_stress_tensors_from_path(root_path, session)
        stress_data[frame_idx, 1] = np.dot(np.dot(normal_root, stress_tensors[0]), normal_root)
        print stress_tensors[0], normal_root, stress_data[frame_idx, 1], frame_idx
        stress_data[frame_idx, 0] = frames[frame_idx].frameValue

    stress_pickle_name = '/scratch/users/erik/scania_gear_analysis/pickles/tooth_root_stresses/stresses_' + name + \
                         '_tooth_' + str(torque) + '_Nm.pkl'

    with open(stress_pickle_name) as stress_pickle:
        pickle.dump(stress_data, stress_pickle)

odb.close()
