import os

import pandas as pd
import parselmouth
from parselmouth.praat import call

ROOT_DIRECTORY = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Dataset/'
OUTPUT_PATH = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/'
directories = ['M', 'MC']
ignore_dir = ['M03', 'MC01/Session2', 'MC02/Session2', 'MC04/Session2']

filter_text = ['feed']


def extract_paths(dir_name, session_name, file_name):
    main_dir = ''
    if 'MC' == dir_name[:2]:
        main_dir = 'MC'
    elif 'M' in dir_name:
        main_dir = 'M'
    else:
        return

    root_path = os.path.join(ROOT_DIRECTORY, main_dir)
    print(root_path)

    if dir_name not in ignore_dir:
        dir_path = os.path.join(root_path, dir_name)
        if dir_name + '/' + session_name not in ignore_dir:
            session_path = os.path.join(dir_path, session_name)
            wav_file_path = session_path + '/' + 'wav_arrayMic' + '/' + file_name.split('.')[0] + '.wav'
            prompt_file_path = session_path + '/' + 'prompts' + '/' + file_name.split('.')[0] + '.txt'
            phn_file_path = session_path + '/' + 'phn_headMic' + '/' + file_name.split('.')[0] + '.phn'
            with open(OUTPUT_PATH + 'file_paths.txt', 'a') as f:
                f.write(main_dir + '\t' + session_name + '\t' + wav_file_path + '\t' + prompt_file_path + '\t' + phn_file_path)
                f.write('\n')


def filter_files():
    df = pd.read_csv(
        r"/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/cleaned_prompt.csv")
    filtered_df = df[df["text"].isin(filter_text)]
    print("Length of the filtered dataframe is ", len(filtered_df))
    if os.path.exists(OUTPUT_PATH + 'file_paths.txt'):
        os.remove(OUTPUT_PATH + 'file_paths.txt')
    f = open(OUTPUT_PATH + 'file_paths.txt', "x")
    for index, row in filtered_df.iterrows():
        extract_paths(row['dir_name'], row['session_name'], row['file_name'])


def main():
    filter_files()


if __name__ == "__main__":
    main()
