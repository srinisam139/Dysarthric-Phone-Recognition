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
import plotly.graph_objects as go
import pickle

json_file_path = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/master_sliced_ema_data.json'

phones_list = ["ih", "iy", "eh", "ah", "ae", "ao", "ay", "ax", "aa", "er", "ey", "uw", "ow", "aw", "uh", "oy", "t", "r",
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
        # print(f" IGNORING {sensor_name}: At least one row is filled with zeros")
        return True
    else:
        # print("No row is filled with zeros.")
        return False


def dtw(root_matrix, other_matrix, root_person, other_person, row_list, phone):
    dtw_distance = dtw_functions.dtw(root_matrix, other_matrix, type_dtw="d",
                                     local_dissimilarity=d.cosine, MTS=True)
    print("#" * 10, f"DTW DISTANCE FOR {root_person} AND {other_person} IS {dtw_distance}", "#" * 10)
    row_list.append({'audio_files': other_person, 'alignment_cost': dtw_distance, 'prompt': 'ema_' + phone})


def stack_matrix(ema_matrix_dict, root_person, phone, master_frame, save=False):
    root_data = {}
    root_matrix = []
    del_col = 5
    for key, value in ema_matrix_dict.items():
        if root_person in key:
            print('*' * 10, f" ROOT PERSON {key}", '*' * 10)
            root_matrix = np.empty((ema_matrix_dict[key][0, :, :].transpose().shape))
            for num, sensor_name in num_to_sensorMapping.items():
                if not check_zero(ema_matrix_dict[key][num, :, :].transpose(), sensor_name):
                    root_data[sensor_name] = ema_matrix_dict[key][num, :, :].transpose()
                else:
                    print('!' * 10, f'CAUTION ROOT DATA {sensor_name} MATRIX HAS ZERO\'S', '!' * 10)
            del ema_matrix_dict[key]
            break
    row_list = []
    for key, value in ema_matrix_dict.items():
        print("*" * 10, f"{key} OTHER SENSOR DATA", "*" * 10)
        root_matrix_copy = root_matrix
        other_matrix = np.empty((value[0, :, :].transpose().shape))
        for sensor_num in num_to_sensorMapping.keys():
            sensor_name = num_to_sensorMapping[sensor_num]
            other_data = value[sensor_num, :, :].transpose()
            if not check_zero(other_data, sensor_name) and sensor_name in root_data.keys():
                root_matrix_copy = np.hstack((root_matrix_copy, root_data[sensor_name]))
                other_matrix = np.hstack((other_matrix, other_data))
            else:
                print('!' * 10, f'{key} OTHER DATA {sensor_name} MATRIX HAS ZERO\'S', '!' * 10)
        root_matrix_copy = root_matrix_copy[:, 5:]
        other_matrix = other_matrix[:, 5:]
        print('-' * 20, f"SHAPE OF THE {root_person} AND {key}", root_matrix_copy.shape, other_matrix.shape, '-' * 20)
        dtw(root_matrix_copy, other_matrix, root_person, key, row_list, phone)
    print(row_list)

    df = pd.DataFrame(row_list)
    master_frame = pd.concat([master_frame, df], ignore_index=True)

    if save:
        fig = px.bar(df, x='person_name', y='alignment_score')
        # Add a title to the graph
        fig.update_layout(
            title_text=f'{root_person} Bar plot of EMA sensor for the phone \'{phone}\'')
        # fig.show()
        root_person_graph_path = os.path.join(output_directory, 'ema_graph', root_person)

        fig.write_image(os.path.join(root_person_graph_path, f'all_sensor_{phone}.png'))

    return master_frame


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
            ema_matrix_dict[key.split('_')[0]] = prep_ema(data[:])
    print("EMA matrix is extracted and sliced successfully")
    return ema_matrix_dict


def sort_dictionary_keys(dictionary):
    sorted_keys = sorted(dictionary.keys())
    sorted_dict = {key: dictionary[key] for key in sorted_keys}
    print("Matrix is sorted successfully")
    return sorted_dict


def get_acoustic_keys(phone_path_dict, root_person, word, phone):
    matrix_dict = {}

    with open(os.path.join(output_directory, 'phone_data', root_person, f'{word}_{phone}_list.pkl'), 'rb') as file:
        loaded_list = pickle.load(file)
    print(loaded_list)
    for key, values in phone_path_dict.items():
        for value in values:
            key_part = key.rsplit('_')[0]
            value_part = value.split('/')[-1].split('.')[0]
            print(key_part, value_part)
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


def line_graph(master_frame, root_person, word):
    with open(os.path.join(output_directory, 'phone_data', root_person, f'{word}_v_phone_df.pkl'), 'rb') as file:
        loaded_df = pickle.load(file)
    master_frame = pd.concat([master_frame, loaded_df], ignore_index=True)
    sorted_data = master_frame.sort_values(by='audio_files')
    fig = px.line(sorted_data, x="audio_files", y="alignment_cost", markers=True, color='prompt')
    fig.update_layout(title_text=f'{root_person} MFCC similarity line chart')
    fig.show()


def bar_chart(master_frame, root_person, word):
    with open(os.path.join(output_directory, 'phone_data', root_person, f'{word}_v_phone_df.pkl'), 'rb') as file:
        loaded_df = pickle.load(file)
    master_frame = pd.concat([master_frame, loaded_df], ignore_index=True)
    # Create traces for each category in each group
    traces = []
    categories = master_frame['prompt'].unique()
    for category in categories:
        group_data = master_frame[master_frame['prompt'] == category]
        trace = go.Bar(
            x=group_data['audio_files'],
            y=group_data['alignment_cost'],
            name=category
        )
        traces.append(trace)

    # Layout settings
    layout = go.Layout(
        title=f'{root_person} similarity bar plot of acoustic_vs_ema phoneme level',
        barmode='group',  # Set barmode to 'group' for grouped bar chart
        xaxis = dict(title='audio_files'),
        yaxis = dict(title='alignment_cost')
    )

    # Create figure and add traces
    fig = go.Figure(data=traces, layout=layout)

    # Show the plot
    #fig.show()

    #Write the image to a locald dir
    fig.write_image(os.path.join(output_directory, 'ema_graph', root_person, word + '_ema' + '.png'))


def main(root_person, phone_list, word):
    ema_path_dict = process_json()
    master_frame = pd.DataFrame()
    for phone in phone_list:
        matrix_path_dict = get_acoustic_keys(ema_path_dict[phone], root_person, word, phone)
        ema_matrix_dict = extract_ema_matrix(matrix_path_dict, phone)
        sorted_ema_dict = sort_dictionary_keys(ema_matrix_dict)
        # print(sorted_ema_dict.keys())
        master_frame = stack_matrix(sorted_ema_dict, root_person, phone, master_frame)
    bar_chart(master_frame, root_person, word)


if __name__ == '__main__':
    main('MC04', ['f', 'iy', 'd'], 'feed')
