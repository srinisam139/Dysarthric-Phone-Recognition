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

json_file_path = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/master_sliced_ema_data.json'

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


def dtw_parallel(word_dict, root_person, word):
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
        row_list.append({'audio_files': key, 'alignment_cost': dtw_distance})
    data = pd.DataFrame(row_list)
    sorted_data = data.sort_values(by='audio_files')
    fig = px.bar(sorted_data, x='audio_files', y='alignment_cost')
    fig.update_layout(title_text=f'{root_person} MFCC similarity Bar plot for \'{word}\'')
    # fig.show()
    fig.write_image(os.path.join(output_directory, 'acoustic_graph', root_person, word + '.png'))


def process_json(filter_word):
    matrix_path_dictionary = {}
    with open(json_file_path, 'r') as json_file:
        data_dict = json.load(json_file)
        for dir_name, values in data_dict.items():
            for person_prompts in values:
                for phone in person_prompts['text']:
                    if phone['prompt'] == filter_word:
                        matrix_path_dictionary[dir_name] = person_prompts['matrix_file_path']
                        break

    return matrix_path_dictionary


def main(root_person, word):
    matrix_dict = process_json(word)
    print(matrix_dict)
    dtw_parallel(matrix_dict, root_person, word)


if __name__ == '__main__':
    main('M03', "feed")
