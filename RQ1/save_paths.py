import os

import pandas as pd
import parselmouth
from parselmouth.praat import call

ROOT_DIRECTORY = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Dataset/'
OUTPUT_PATH = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/'
directories = ['M', 'MC']

filter_text = ['feed', 'horn', 'the quick brown fox jumps over the lazy dog','don\'t ask me to carry an oily rag like that']


def extract_paths(dir_name, session_name, file_name, text, row_list, added_directories):
    main_dir = ''
    if 'MC' == dir_name[:2]:
        main_dir = 'MC'
    elif 'M' in dir_name:
        main_dir = 'M'
    else:
        return

    root_path = os.path.join(ROOT_DIRECTORY, main_dir)
    print(root_path + '\t' + file_name.split(".")[0])

    if dir_name not in added_directories:

        dir_path = os.path.join(root_path, dir_name)

        session_path = os.path.join(dir_path, session_name)
        if os.path.exists(session_path + '/' + 'wav_headMic' + '/' + file_name.split('.')[0] + '.wav'):
            wav_file_path = session_path + '/' + 'wav_headMic' + '/' + file_name.split('.')[0] + '.wav'
        else:
            wav_file_path = session_path + '/' + 'wav_arrayMic' + '/' + file_name.split('.')[0] + '.wav'
        prompt_file_path = session_path + '/' + 'prompts' + '/' + file_name.split('.')[0] + '.txt'
        pos_file_path = None
        if os.path.exists(session_path + '/' + 'pos' + '/' + file_name.split('.')[0] + '.pos'):
            pos_file_path = True
            pos_file_path = session_path + '/' + 'pos' + '/' + file_name.split('.')[0] + '.pos'
        phn_file_path = None  # Initialize phn_file_path
        for phn_dir in ['phn_arrayMic', 'phn_headMic']:
            phn_file_candidates = [
                os.path.join(session_path, phn_dir, file_name.split('.')[0] + '.phn'),
                os.path.join(session_path, phn_dir, file_name.split('.')[0] + '.PHN')
            ]
            for candidate in phn_file_candidates:
                if os.path.exists(candidate):
                    phn_file_path = candidate
                    break

        if phn_file_path is not None and pos_file_path is not None:
            # Append file paths to file_paths.txt
            """with open(os.path.join(OUTPUT_PATH, 'file_paths.txt'), 'a') as f:
                f.write(
                    f'{dir_name}\t{session_name}\t{file_name.split(".")[0]}\t{wav_file_path}\t{prompt_file_path}\t{phn_file_path}\n')"""
            new_data = {'person_name': dir_name, 'session_name': session_name, 'file_number': file_name.split(".")[0],
                        'text': text,
                        'wav_file_path': wav_file_path, 'prompt_file_path': prompt_file_path,
                        'phn_file_path': phn_file_path,
                        'pos_file_path': pos_file_path}
            row_list.append(new_data)
            added_directories.append(dir_name)


def filter_files():
    df = pd.read_csv(
        r"/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/cleaned_prompt.csv")

    if os.path.exists(OUTPUT_PATH + 'file_paths.csv'):
        os.remove(OUTPUT_PATH + 'file_paths.csv')

    new_df = pd.DataFrame(
        columns=['person_name', 'session_name', 'file_number', 'text', 'wav_file_path', 'prompt_file_path',
                 'phn_file_path', 'pos_file_path'])

    row_list = []  # Create a list to store rows

    for text in filter_text:
        filtered_df = df[df["text"] == text]
        print("Filtering the text ", text)
        print("Length of the filtered dataframe is ", len(filtered_df))
        added_directories = []
        for index, row in filtered_df.iterrows():
            extract_paths(row['dir_name'], row['session_name'], row['file_name'], row['text'], row_list,
                          added_directories)

    # Concatenate the list of rows into a DataFrame
    new_df = pd.concat([new_df, pd.DataFrame(row_list)], ignore_index=True)

    new_df.to_csv(os.path.join(OUTPUT_PATH, 'file_paths_temp.csv'), index=False)


def main():
    filter_files()


if __name__ == "__main__":
    main()
