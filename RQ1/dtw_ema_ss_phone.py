import h5py
import json
import random
import numpy as np
import pandas as pd
from dtwParallel import dtw_functions
from scipy.spatial import distance as d
import os
import sys
import plotly.express as px
import pickle

json_file_path = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/master_sliced_ema_data.json'

phones_list = ["ih", "iy", "eh", "ah", "ae", "ao", "ay", "ay", "aa", "er", "ey", "uw", "ow", "aw", "uh", "oy", "t", "r",
               "n", "l", "s", "d", "k", "p", "m", "z", "w", "b", "f", "dh", "g", "v", "y", "ng", "sh", "ch", "jh", "th",
               "zh", "h", "hh"]

prompt_to_code = {'feed': 'T1', 'horn': 'T2', 'the quick brown fox jumps over the lazy dog': 'T3',
                  'dont ask me to carry an oily rag like that': 'T4'}
code_to_prompt = {'T1': 'feed', 'T2': 'horn', 'T3': 'the quick brown fox jumps over the lazy dog',
                  'T4': 'dont ask me to carry an oily rag like that'}

sensor_list = [1, 2, 3, 6, 7, 9, 10]

output_directory = '/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/'

num_to_sensorMapping = {0: 'Tongue back', 1: 'Tongue middle', 2: 'Tongue tip',
                        3: 'Upper lip', 4: 'Lower lip', 5: 'Left lip',
                        6: 'Right lip'}


def check_zero(matrix, sensor_name):
    # Check if any row is filled with zeros
    any_row_filled_with_zeros = np.any((matrix == 0).all(axis=1))

    # Print the result
    if any_row_filled_with_zeros:
        #print(f" IGNORING {sensor_name}: At least one row is filled with zeros")
        return True
    else:
        #print("No row is filled with zeros.")
        return False


def compare_matrix(ema_matrix_dict, root_person, phone):
    root_data = {}

    for key, value in ema_matrix_dict.items():
        if root_person in key:
            print('*'*10, f" ROOT PERSON {key}", '*'*10)
            for num, sensor_name in num_to_sensorMapping.items():
                if not check_zero(ema_matrix_dict[key][num, :, :].transpose(), sensor_name):
                    root_data[sensor_name] = ema_matrix_dict[key][num, :, :].transpose()
                else:
                    print('!' * 10, f'CAUTION ROOT DATA {sensor_name} MATRIX HAS ZERO\'S', '!' * 10)
            del ema_matrix_dict[key]
            break

    for sensor_num in num_to_sensorMapping.keys():
        row_list = []
        sensor_flag = False
        for key, value in ema_matrix_dict.items():
            print("*" * 10, f"{key} OTHER SENSOR DATA", "*" * 10)
            sensor_name = num_to_sensorMapping[sensor_num]
            other_data = value[sensor_num, :, :].transpose()
            if not check_zero(other_data, sensor_name) and sensor_name in root_data.keys():
                sensor_flag = True
                #print("Sensor name is ", sensor_name, "\tSensor data shape is ", other_data.shape)
                dtw_distance = dtw_functions.dtw(root_data[sensor_name], other_data, type_dtw="d",
                                                 local_dissimilarity=d.cosine, MTS=True)
                print("#" * 10, f"DTW DISTANCE FOR {sensor_name} between {root_person} AND {key} IS {dtw_distance}", "#" * 10)
                row_list.append({'person_name': key, 'alignment_score': dtw_distance})
            else:
                print('!' * 10, f' OTHER DATA {sensor_name} MATRIX HAS ZERO\'S', '!' * 10)

        if sensor_flag:
            df = pd.DataFrame(row_list)
            fig = px.bar(df, x='person_name', y='alignment_score')
            # Add a title to the graph
            fig.update_layout(
                title_text=f'{root_person} Bar plot of {num_to_sensorMapping[sensor_num]} for the phone \'{phone}\'')
            # fig.show()
            root_person_graph_path = os.path.join(output_directory, 'ema_graph', root_person)
            if num_to_sensorMapping[sensor_num] not in os.listdir(root_person_graph_path):
                # Create the directory
                os.makedirs(os.path.join(root_person_graph_path, num_to_sensorMapping[sensor_num]), exist_ok=False)
            fig.write_image(os.path.join(root_person_graph_path, num_to_sensorMapping[sensor_num], phone + '.png'))


def prep_ema(data):
    # print("Shape of the ema before slicing ", data[:].shape)
    sliced_ema_fd = data[sensor_list, :, :]
    sliced_ema_sd = sliced_ema_fd[:, :3, :]

    # print('Shape of the sliced matrix is ', sliced_ema_sd.shape)

    return sliced_ema_sd


def extract_ema_matrix(ema_dict, phone):

    ema_matrix_dict = {}
    for key, ema_file_path in ema_dict.items():
        with h5py.File(ema_file_path, 'r') as file:
            data = file[phone]
            ema_matrix_dict[key] = prep_ema(data[:])
    print("EMA matrix is extracted and sliced successfully")
    return ema_matrix_dict


def sort_dictionary_keys(dictionary):
    sorted_keys = sorted(dictionary.keys())
    sorted_dict = {key: dictionary[key] for key in sorted_keys}
    print("Matrix is sorted successfully")
    return sorted_dict


def get_acoustic_keys(phone_path_dict, root_person, phone):
    matrix_dict = {}

    with open(os.path.join(output_directory, 'phone_data', root_person, f'{phone}_list.pkl'), 'rb') as file:
        loaded_list = pickle.load(file)

    for key, values in phone_path_dict.items():
        for value in values:
            key_part = key.rsplit('_', 1)[0]
            value_part = value.split('/')[-1].split('.')[0]
            if key_part + '_' + value_part in loaded_list:
                matrix_dict[key] = value
    print("Acoustic matrix extracted successfully")
    return matrix_dict


def process_json():
    # Create a dictionary with keys and empty lists as values
    phones_dictionary = {key: [] for key in phones_list}
    person_dictionary = {}
    with open(json_file_path, 'r') as json_file:
        data_dict = json.load(json_file)
        for dir_name, values in data_dict.items():
            for person_prompts in values:
                # print(type(person_prompts), dir_name)
                for phones in person_prompts['text']:
                    # print(phones)
                    code = prompt_to_code[phones['prompt']]
                    if dir_name + '_' + code + '_' + phones['phone'] not in person_dictionary.keys():
                        person_dictionary[dir_name + '_' + code + '_' + phones['phone']] = []
                    # print("KEY ", dir_name + '_' + phones['phone'], "VALUE ", phones['ema_file_path'])
                    person_dictionary[dir_name + '_' + code + '_' + phones['phone']].append(phones['ema_file_path'])

        for root_key in phones_dictionary.keys():
            phones_dictionary[root_key] = {key: value for key, value in person_dictionary.items() if
                                           root_key == key.split('_')[2]}

    return phones_dictionary


def main(root_person, phone):
    ema_path_dict = process_json()
    matrix_path_dict = get_acoustic_keys(ema_path_dict[phone], root_person, phone)
    ema_matrix_dict = extract_ema_matrix(matrix_path_dict, phone)
    sorted_ema_dict = sort_dictionary_keys(ema_matrix_dict)
    compare_matrix(sorted_ema_dict, root_person, phone)


if __name__ == '__main__':
    main('MC01', 'iy')
