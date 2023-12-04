import parselmouth
from parselmouth.praat import call
import pandas as pd
import os

directories = ['M','MC']
ROOT_DIRECTORY = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Dataset/'

phn_dictionary = {}


def count_phones(file_path):
    try:
        # Attempt to perform the operation that might raise the exception
        # For example, trying to load a TextGrid file
        tg = parselmouth.TextGrid.read(file_path)
        interval_count = call(tg, "Get number of intervals", 1)

        for n in range(1, interval_count + 1):
            label = call(tg, "Get label of interval", 1, n)
            if label not in phn_dictionary:
                phn_dictionary[label] = 1
            else:
                phn_dictionary[label] += 1
        # If successful, continue with the rest of your code here

    except parselmouth.PraatError as e:
        # Handle the specific exception
        print(f"Error: {e}")
        print(f"File '{file_path}' contains no audio data.")


def extract_phone_paths():
    for dir_name in directories:
        sub_directory = os.path.join(ROOT_DIRECTORY, dir_name)

        for sub_dir_name in os.listdir(sub_directory):

            if not sub_dir_name.startswith('.'):
                partial_path = os.path.join(sub_directory, sub_dir_name)
                # print(partial_path)
                for session_name in os.listdir(partial_path):
                    if session_name.startswith("Session"):

                        session_path = os.path.join(partial_path, session_name)
                        # print(session_path)
                        file_name = ''
                        if os.path.isdir(os.path.join(session_path, 'phn_arrayMic')):
                            file_name = os.path.join(session_path, 'phn_arrayMic')
                        elif os.path.isdir(os.path.join(session_path, 'phn_headMic')):
                            file_name = os.path.join(session_path, 'phn_headMic')

                        if file_name != '':
                            phn_dir = os.path.join(session_path, file_name)

                            for phn_file in os.listdir(phn_dir):
                                # print(phn_file)
                                if len(phn_file.split('.')[0]) == 4:
                                    full_path = os.path.join(phn_dir, phn_file)

                                    print(full_path)

                                    count_phones(full_path)


extract_phone_paths()

print(len(phn_dictionary))

# Get the top 50 items based on counts
top_90_items = sorted(phn_dictionary.items(), key=lambda x: x[1], reverse=True)[0:90]

# Print the top 50 items
for item, count in top_90_items:
    print(f"{item}: {count}")