import pandas as pd
import numpy as np
import re

OUTPUT_PATH = r'/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/'

prompt_df = pd.read_csv(OUTPUT_PATH + 'prompts.csv')
print(prompt_df.columns)

print("Number of prompts in the TORGO file", len(prompt_df))


def reg_exp(text):
    # Check for ".jpg" within words and remove the entire string
    if re.search(r'\b\S*\.jpg\S*\b', text):
        text = ""

    # Check for a newline at the end and remove it
    if re.search(r'\n$', text):
        text = re.sub(r'\n$', '', text)

    # Check for a single dot at the end and remove it
    if re.search(r'\.', text):
        text = re.sub(r'\.', '', text)

    if re.search(r'xxx|xx', text):
        text = re.sub(r'xxx|xx', '', text)

    return text.strip()


"""
This function helps to clean the text files by analyzing the prompts. By removing the unclear texts from
the prompt.csv file, .wav files can be clearly extracted further.
"""


def clean_text(df):
    # Few prompts which are named 'xxx' are replaced with np.nan because they don't represent
    # any sound.
    df['Text'] = df['Text'].apply(lambda x: reg_exp(x))
    df['Text'].replace('', np.nan, inplace=True)
    df.dropna(subset=['Text'], inplace=True)
    df['Text'] = df['Text'].str.lower()
    print(df['Text'].tolist())
    print("Printing the length of the file after removing empty values", len(df))
    return df


def save_csv(df):
    df.to_csv(OUTPUT_PATH + "cleaned_prompt.csv")


def main():
    cleaned_df = clean_text(prompt_df)
    save_csv(cleaned_df)


if __name__ == "__main__":
    main()
