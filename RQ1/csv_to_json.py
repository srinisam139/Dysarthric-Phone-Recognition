import csv
import json
import os
import csv
import re
import numpy as np
import shlex

csv_file_path = '/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/file_paths.csv'
json_file_path = '/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/master_data.json'
directory = "/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/"


def convert_csv_to_json():
    # Read the CSV file and convert it to a list of dictionaries
    csv_data = []
    csv_data_grouped = {}
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            name = row['person_name']
            if name not in csv_data_grouped:
                csv_data_grouped[name] = []
            csv_data_grouped[name].append(row)

    # Write the list of dictionaries to a JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(csv_data_grouped, json_file, indent=2)

    print(f'CSV file "{csv_file_path}" converted to JSON file "{json_file_path}".')


def extract_sliced_matrix(sub_dir_path, save_dir_name, prompt, phone, start_frame, end_frame, count_dict):
    for dir_name in os.listdir(sub_dir_path):
        if (os.path.isfile(os.path.join(sub_dir_path, dir_name)) and dir_name.split('_')[
            1] == prompt and not dir_name.endswith('.npy')):
            # print(prompt)
            matrix_path = os.path.join(sub_dir_path, dir_name)
            if not os.path.exists(os.path.join(sub_dir_path, dir_name + '.npy')):
                matrix = np.loadtxt(matrix_path)
                np.save(os.path.join(sub_dir_path, dir_name + '.npy'), matrix)
                print("matrix saved")
            else:
                matrix = np.load(os.path.join(sub_dir_path, dir_name + '.npy'))
            # print(start_frame), round(float(end_frame)))
            sliced_matrix = matrix[:, round(float(start_frame)):round(float(end_frame))]
            if not os.path.exists(sub_dir_path + '/' + prompt):
                os.makedirs(sub_dir_path + '/' + prompt)
            sliced_matrix_path = os.path.join(sub_dir_path, prompt, phone + '_sliced' + '.npy')
            if os.path.exists(sliced_matrix_path):
                print(save_dir_name + '_' + prompt + '_' + phone)
                count_dict[save_dir_name + '_' + prompt + '_' + phone] += 1
                value = count_dict[save_dir_name + '_' + prompt + '_' + phone]
                sliced_matrix_path = os.path.join(sub_dir_path, prompt, phone + '_sliced' + '_' + str(value) + '.npy')
            else:
                count_dict[save_dir_name + '_' + prompt + '_' + phone] = 1
            np.save(sliced_matrix_path, sliced_matrix)
            return sliced_matrix_path


def extract_frame(phone_dir, json_data, save=True):
    for dir_name in os.listdir(phone_dir):
        if dir_name != ".DS_Store":
            print("*" * 10, dir_name, "*" * 10)
            text_details = {}
            counter_dictionary = {}
            sub_dir_path = os.path.join(phone_dir, dir_name, 'matrix')
            time_frame_path = os.path.join(phone_dir, dir_name, 'matrix', dir_name + '_time_frame.txt')
            if os.path.exists(time_frame_path):
                # print(dir_name+'_time_frame.txt')

                with open(time_frame_path, 'r') as file:
                    for line in file:
                        single_line = line.strip()
                        # print(single_line)
                        word = ' '.join(re.findall(r"'([^']*)'", single_line))
                        phone = shlex.split(single_line)[1].split('-')[1]
                        start_time = shlex.split(single_line)[2].split(':')[1]
                        end_time = shlex.split(single_line)[3].split(':')[1]
                        start_frame = shlex.split(single_line)[4].split(':')[1]
                        end_frame = shlex.split(single_line)[5].split(':')[1]
                        # print(f"prompt: {word}, phone: {phone}, start_time: {start_time}, end_time: {end_time}, "
                        # f"start_frame: {start_frame}, end_frame: {end_frame}")
                        if word not in text_details.keys():
                            text_details[word] = []

                        sliced_matrix_path = extract_sliced_matrix(sub_dir_path, dir_name, word, phone, start_frame,
                                                                   end_frame, counter_dictionary)

                        text_details[word].append(
                            {'prompt': word, 'phone': phone, 'start_time': start_time, 'end_time': end_time,
                             'start_frame': start_frame, 'end_frame': end_frame,
                             'sliced_matrix_path': sliced_matrix_path})

                for index, person_details in enumerate(json_data[dir_name]):
                    json_data[dir_name][index]['matrix_file_path'] = os.path.join(sub_dir_path, dir_name + '_' + text_details[person_details['text']][0]['prompt'] + '.npy')
                    json_data[dir_name][index]['text'] = text_details[person_details['text']]
                # print(json_data)
    if save:
        with open(directory + '/master_sliced_data.json', 'w') as json_file:
            json.dump(json_data, json_file, indent=2)


def main():
    convert_csv_to_json()
    json_file = open(json_file_path, 'r')
    json_data = json.load(json_file)
    extract_frame(directory + 'phone_data', json_data)
    json_file.close()


if __name__ == '__main__':
    main()
