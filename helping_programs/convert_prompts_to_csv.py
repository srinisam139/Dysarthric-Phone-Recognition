import os
import csv


# Function to process a session directory
def extract_prompt(root_name, session_dir, csv_writer):
    prompts_dir = os.path.join(session_dir, "prompts")

    if not os.path.exists(prompts_dir):
        return

    for root, _, files in os.walk(prompts_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as txt_file:
                    text = txt_file.read()
                    csv_writer.writerow([root_name, file, text])


def process_session(directory, path, csv_writer):
    for dir_name in os.listdir(path):
        if dir_name.startswith("Session"):
            session_dir = os.path.join(path, dir_name)
            extract_prompt(directory, session_dir, csv_writer)


def process_directory(directory, dir, csv_writer):
    for dir_name in os.listdir(dir):
        if dir_name.startswith(directory):
            sub_dir = os.path.join(dir, dir_name)
            process_session(directory, sub_dir, csv_writer)


# Main program
root_directory = "/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Dysarthric-Phone-Recognition/Dataset"
directories = ['F', 'FC', 'M', 'MC']
csv_file = "prompts.csv"

with open(csv_file, "w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["File Name", "Text"])

    for directory in directories:
        dir_path = os.path.join(root_directory, directory)
        if os.path.exists(dir_path):
            process_directory(directory, dir_path, csv_writer)
        else:
            print(f"The '{directory}' directory does not exist.")

print("Process completed and data is saved to 'output.csv'.")
