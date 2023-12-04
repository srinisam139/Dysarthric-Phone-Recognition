import numpy as np
from tslearn.clustering import TimeSeriesKMeans
from tslearn.preprocessing import TimeSeriesScalerMinMax
from tslearn.datasets import CachedDatasets
from tslearn.clustering import silhouette_score
import json
import collections

phones_list = ["ih", "iy", "eh", "ah", "ae", "ao", "ay", "ay", "aa", "er", "ey", "uw", "ow", "aw", "uh", "oy", "t", "r",
               "n",
               "l", "s", "d", "k", "p", "m", "z", "w", "b", "f", "dh", "g", "v", "y", "ng", "sh", "ch", "jh", "th",
               "zh",
               "h", "hh"]

json_file_path = '/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/master_sliced_ema_data.json'

prompt_to_code = {'feed': 'T1', 'horn': 'T2', 'the quick brown fox jumps over the lazy dog': 'T3',
                  'dont ask me to carry an oily rag like that': 'T4'}
code_to_prompt = {'T1': 'feed', 'T2': 'horn', 'T3': 'the quick brown fox jumps over the lazy dog',
                  'T4': 'dont ask me to carry an oily rag like that'}


def timeseriesKMeans(stacked_matrix):
    km = TimeSeriesKMeans(n_clusters=3, metric="softdtw", max_iter=50, max_iter_barycenter=30, random_state=4)
    pred = km.fit_predict(stacked_matrix)
    print(pred)
    score_ss = silhouette_score(stacked_matrix, pred, metric="softdtw")
    print(score_ss)

    return pred


def stack_mfcc(flat_mfcc_dict):
    X = []
    y_label = []
    for key, values in flat_mfcc_dict.items():
        for value in values:
            y_label.append(key)
            matrix = np.load(value)
            mat_t = matrix.transpose()
            X.append(mat_t)
    print("Length of labelled data is ", len(y_label))

    # print(len(X), len(y_label))

    # Find the maximum length of time series
    max_length = max(len(ts) for ts in X)

    # Pad or truncate each time series to the maximum length
    padded_time_series_list = [np.pad(ts, ((0, max_length - len(ts)), (0, 0)), 'constant') for ts in X]

    print(padded_time_series_list[0].shape, padded_time_series_list[1].shape)

    scaled_time_series_list = [TimeSeriesScalerMinMax().fit_transform(ts) for ts in padded_time_series_list]

    print(scaled_time_series_list[0].shape, scaled_time_series_list[1].shape)

    reshaped_time_series_list = [np.squeeze(ts, axis=-1) for ts in scaled_time_series_list]

    print(reshaped_time_series_list[0].shape, reshaped_time_series_list[1].shape)

    stacked_matrices = np.stack(reshaped_time_series_list)

    return stacked_matrices, y_label


def flat_mfcc(original_dict):
    flattened_dict = {}

    for key, value in original_dict.items():
        flattened_list = []
        for item in value:
            if isinstance(item, list):
                flattened_list.extend(item)
            else:
                flattened_list.append(item)
        flattened_dict[key] = flattened_list

    print(flattened_dict)
    return flattened_dict


def process_json():
    # Create a dictionary with keys and empty lists as values
    phones_dictionary = {key: [] for key in phones_list}
    person_dictionary = {}
    with open(json_file_path, 'r') as json_file:
        data_dict = json.load(json_file)
        for dir_name, values in data_dict.items():
            for person_prompts in values:
                for phones in person_prompts['text']:
                    # print(phones)
                    code = prompt_to_code[phones['prompt']]
                    if dir_name + '_' + code + '_' + phones['phone'] not in person_dictionary.keys():
                        person_dictionary[dir_name + '_' + code + '_' + phones['phone']] = []
                    # print("KEY ", dir_name + '_' + code + '_' + phones['phone'], "VALUE ", phones['sliced_matrix_path'])
                    person_dictionary[dir_name + '_' + code + '_' + phones['phone']].append(
                        phones['sliced_matrix_path'])

        for root_key in phones_dictionary.keys():
            phones_dictionary[root_key] = [value for key, value in person_dictionary.items() if
                                           root_key == key.split('_')[2]]

    return phones_dictionary


def high_freq_keys(phone_dict, count, n):
    high_freq_dict = {}
    for key, value in count.items():
        if value > n:
            high_freq_dict[key] = phone_dict[key]
    return high_freq_dict


def main():
    mfcc_dict = process_json()
    flat_mfcc_paths = flat_mfcc(mfcc_dict)
    phones_count = {key: len(value) for key, value in flat_mfcc_paths.items() if value != []}
    print(phones_count)
    freq_mfcc_dict = high_freq_keys(flat_mfcc_paths, phones_count, 24)
    print(freq_mfcc_dict.keys())
    stacked_matrices, y_label = stack_mfcc(freq_mfcc_dict)
    pred = timeseriesKMeans(stacked_matrices)
    frequency = collections.Counter(pred)
    print(frequency)


if __name__ == '__main__':
    main()
