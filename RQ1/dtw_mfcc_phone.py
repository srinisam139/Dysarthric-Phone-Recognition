import numpy as np
import os
import random
import scipy.spatial.distance as dist
import pandas as pd
import plotly.express as px
import json
import pickle
from dtwParallel import dtw_functions
from scipy.spatial import distance as d

json_file_path = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/master_sliced_data.json'

phones_list = ["ih", "iy", "eh", "ah", "ae", "ao", "ay", "ay", "aa", "er", "ey", "uw", "ow", "aw", "uh", "oy", "t", "r",
               "n",
               "l", "s", "d", "k", "p", "m", "z", "w", "b", "f", "dh", "g", "v", "y", "ng", "sh", "ch", "jh", "th",
               "zh",
               "h", "hh"]

prompt_to_code = {'feed': 'T1', 'horn': 'T2', 'the quick brown fox jumps over the lazy dog': 'T3',
                  'dont ask me to carry an oily rag like that': 'T4'}
code_to_prompt = {'T1': 'feed', 'T2': 'horn', 'T3': 'the quick brown fox jumps over the lazy dog',
                  'T4': 'dont ask me to carry an oily rag like that'}

output_directory = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/'

save_key = []


def dtw(dist_mat):
    """
    Find minimum-cost path through matrix `dist_mat` using dynamic programming.

    The cost of a path is defined as the sum of the matrix entries on that
    path. See the following for details of the algorithm:

    - http://en.wikipedia.org/wiki/Dynamic_time_warping
    - https://www.ee.columbia.edu/~dpwe/resources/matlab/dtw/dp.m

    The notation in the first reference was followed, while Dan Ellis's code
    (second reference) was used to check for correctness. Returns a list of
    path indices and the cost matrix.
    """

    N, M = dist_mat.shape

    # Initialize the cost matrix
    cost_mat = np.zeros((N + 1, M + 1))
    for i in range(1, N + 1):
        cost_mat[i, 0] = np.inf
    for i in range(1, M + 1):
        cost_mat[0, i] = np.inf

    # Fill the cost matrix while keeping traceback information
    traceback_mat = np.zeros((N, M))
    for i in range(N):
        for j in range(M):
            penalty = [
                cost_mat[i, j],  # match (0)
                cost_mat[i, j + 1],  # insertion (1)
                cost_mat[i + 1, j]]  # deletion (2)
            i_penalty = np.argmin(penalty)
            cost_mat[i + 1, j + 1] = dist_mat[i, j] + penalty[i_penalty]
            traceback_mat[i, j] = i_penalty

    # Traceback from bottom right
    i = N - 1
    j = M - 1
    path = [(i, j)]
    while i > 0 or j > 0:
        tb_type = traceback_mat[i, j]
        if tb_type == 0:
            # Match
            i = i - 1
            j = j - 1
        elif tb_type == 1:
            # Insertion
            i = i - 1
        elif tb_type == 2:
            # Deletion
            j = j - 1
        path.append((i, j))

    # Strip infinity edges from cost_mat before returning
    cost_mat = cost_mat[1:, 1:]
    return path[::-1], cost_mat


def random_choice(my_dict):
    random_key = random.choice(list(my_dict.keys()))
    random_value = random.choice(my_dict[random_key])

    return random_key, random_value


def save_keys(my_dict, root_person, phone, word):
    save_list = []

    for key, value in my_dict.items():
        # Extract 'M04_T3' from the key
        key_parts = key.rsplit('_', 1)[0]  # Assuming the format is consistent

        # Extract 'dh_sliced_2' from the value
        value_parts = value.split('/')[-1].split('.')[0]

        save_list.append(key_parts + '_' + value_parts)

    with open(os.path.join(output_directory, 'phone_data', root_person, f'{word}_{phone}_list.pkl'), 'wb') as file:
        pickle.dump(save_list, file)


def get_unique_matrix_dict(phone_dict):
    phone_set = set()
    matrix_dict = {}
    for main_key, value in phone_dict.items():
        unique_key = main_key.rsplit('_', 1)[0]
        if unique_key not in phone_set and 'T1' in unique_key:
            phone_set.add(unique_key)
            unique_dict = {key: phone_dict[key] for key in phone_dict.keys() if unique_key in key}
            unique_key_list, unique_value = random_choice(unique_dict)
            matrix_dict[unique_key.split('_')[0]] = unique_value
    return matrix_dict


def sort_dictionary(dictionary_list):
    sorted_data = sorted(dictionary_list, key=lambda x: x['person_name'])
    print(sorted_data)
    # return sorted_data


def compare_phone_matrix(phone_dict, root_person, phone, master_frame, save=False):
    root_matrix = []

    print("length before deleting", len(phone_dict))
    for key, value in phone_dict.items():
        if root_person in key:
            root_matrix = np.load(value)
            del phone_dict[key]
            break
    print("length after deleting", len(phone_dict))

    alignment_cost = []

    for key, value in phone_dict.items():

        read_matrix = np.load(value)
        # Distance matrix
        x_seq = root_matrix.T
        # print("Transposed x_seq matrix shape ", x_seq.shape)
        y_seq = read_matrix.T
        # print("Transposed  y_seq matrix shape ", y_seq.shape)

        dist_mat = dist.cdist(x_seq, y_seq, "cosine")
        # print("Spatial distance shape", dist_mat.shape)

        try:
            path, cost_mat = dtw(dist_mat)

            print("Alignment cost: {:.4f}".format(cost_mat[-1, -1]))
            alignment_cost.append(cost_mat[-1, -1])
            M = y_seq.shape[0]
            N = x_seq.shape[0]
            print(
                "Normalized alignment cost: {:.8f}".format(
                    cost_mat[-1, -1] / (M + N))
            )
            print()
        except Exception as E:
            alignment_cost.append(0)

    data = pd.DataFrame({'audio_files': phone_dict.keys(), 'alignment_cost': alignment_cost, 'prompt': phone})
    master_frame = pd.concat([master_frame, data], ignore_index=True)
    if save:
        sorted_data = data.sort_values(by='audio_files')
        fig = px.bar(sorted_data, x='audio_files', y='alignment_cost')
        fig.update_layout(title_text=f'{root_person} MFCC similarity Bar plot for \'{phone}\'')
        # fig.show()
        fig.write_image(os.path.join(output_directory, 'acoustic_graph', root_person, phone + '_T1' + '.png'))

    return master_frame


def compare_word_matrix(word_dict, root_person, word, master_frame, save=False):
    root_matrix = []

    print("length before deleting", len(word_dict))
    for key, value in word_dict.items():
        if root_person in key:
            root_matrix = np.load(value)
            del word_dict[key]
            break
    print("length after deleting", len(word_dict))
    row_list = []
    for key, value in word_dict.items():
        read_matrix = np.load(value)
        # Distance matrix
        x_seq = root_matrix.T
        # print("Transposed x_seq matrix shape ", x_seq.shape)
        y_seq = read_matrix.T

        print(x_seq.shape, y_seq.shape)

        dtw_distance = dtw_functions.dtw(x_seq, y_seq, type_dtw="d", local_dissimilarity=d.cosine, MTS=True)

        print("#" * 10, f"DTW DISTANCE FOR '{word}' between {root_person} AND {key} IS {dtw_distance}", "#" * 10)
        row_list.append({'audio_files': key, 'alignment_cost': dtw_distance, 'prompt': word})

    data = pd.DataFrame(row_list)
    master_frame = pd.concat([master_frame, data], ignore_index=True)
    if save:
        sorted_data = data.sort_values(by='audio_files')
        fig = px.bar(sorted_data, x='audio_files', y='alignment_cost')
        fig.update_layout(title_text=f'{root_person} MFCC similarity Bar plot for \'{word}\'')
        # fig.show()
        fig.write_image(os.path.join(output_directory, 'acoustic_graph', root_person, word + '.png'))

    return master_frame


def process_json(filter_word):
    word_dictionary = {}
    word_set = set()
    # Create a dictionary with keys and empty lists as values
    phones_dictionary = {key: [] for key in phones_list}
    person_dictionary = {}
    with open(json_file_path, 'r') as json_file:
        data_dict = json.load(json_file)
        for dir_name, values in data_dict.items():
            for person_prompts in values:
                for phones in person_prompts['text']:
                    if phones['prompt'] == filter_word and dir_name not in word_set:
                        word_set.add(dir_name)
                        word_dictionary[dir_name] = person_prompts['matrix_file_path']
                    # print(phones)
                    code = prompt_to_code[phones['prompt']]
                    if dir_name + '_' + code + '_' + phones['phone'] not in person_dictionary.keys():
                        person_dictionary[dir_name + '_' + code + '_' + phones['phone']] = []
                    # print("KEY ", dir_name + '_' + code + '_' + phones['phone'], "VALUE ", phones['sliced_matrix_path'])
                    person_dictionary[dir_name + '_' + code + '_' + phones['phone']].append(
                        phones['sliced_matrix_path'])
        for root_key in phones_dictionary.keys():
            phones_dictionary[root_key] = {key: value for key, value in person_dictionary.items() if
                                           root_key == key.split('_')[2]}

    return phones_dictionary, word_dictionary


def line_graph(master_frame, root_person, word):
    sorted_data = master_frame.sort_values(by='audio_files')
    fig = px.line(sorted_data, x="audio_files", y="alignment_cost", markers=True, color='prompt')
    fig.update_layout(title_text=f'{root_person} MFCC similarity line chart')
    # fig.show()
    fig.write_image(os.path.join(output_directory, 'acoustic_graph', root_person, word + '_v_phone' + '.png'))


def save_df(df, root_person, word):
    with open(os.path.join(output_directory, 'phone_data', root_person, f'{word}_v_phone_df.pkl'), 'wb') as file:
        pickle.dump(df, file)


def main(root_person, phone_list, word):
    phones_dict, word_dict = process_json(word)
    print(phones_dict, word_dict)
    master_frame = pd.DataFrame()
    master_frame = compare_word_matrix(word_dict, root_person, word, master_frame)
    for phone in phone_list:
        unique_phone_dict = get_unique_matrix_dict(phones_dict[phone])
        save_keys(unique_phone_dict, root_person, phone, word)
        master_frame = compare_phone_matrix(unique_phone_dict, root_person, phone, master_frame)
    save_df(master_frame,root_person,word)
    line_graph(master_frame, root_person, word)


if __name__ == '__main__':
    main("MC05", ['f', 'iy', 'd'], 'feed')
