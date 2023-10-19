import numpy as np
import os
import csv
import numpy
import scipy.spatial.distance as dist
import pandas as pd
import plotly.express as px


def dp(dist_mat):
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
    return (path[::-1], cost_mat)


def compare_matrix(directory, matrix):
    root_matrix = np.load(directory + matrix)

    # List all files in the directory
    files = os.listdir(directory)

    # Filter the files to find the one ending with '.npy'
    npy_files = [file for file in files if file.endswith('.npy') and 'sliced' in file.split('.')[0].split('_')]
    print(npy_files)
    alignment_cost = []
    modified_filenames = [filename.replace('.npy', '') for filename in npy_files]
    # Iterate through the .npy files
    for npy_file in npy_files:
        full_path = os.path.join(directory, npy_file)
        print(f"Processing {npy_file}")

        read_matrix = np.load(directory + npy_file)
        # Distance matrix
        x_seq = root_matrix.T
        # print("Transposed x_seq matrix shape ", x_seq.shape)
        y_seq = read_matrix.T
        # print("Transposed  y_seq matrix shape ", y_seq.shape)

        dist_mat = dist.cdist(x_seq, y_seq, "cosine")
        # print("Spatial distance shape", dist_mat.shape)
        cost_mat = []
        try:
            path, cost_mat = dp(dist_mat)

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

    data = pd.DataFrame({'audio_files': modified_filenames, 'alignment_cost': alignment_cost})
    fig = px.bar(data, x='audio_files', y='alignment_cost')
        #fig.show()
    fig.write_image("/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/matrix/Images/praat_sliced.png")


def save_matrix(directory):
    for dir_name in os.listdir(directory):
        start_frame = 0
        end_frame = 0
        words = dir_name.split("_")
        if "frames" in words:
            # Open the file and read it with tab as the delimiter
            with open(directory + dir_name, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter='\t')
                # Iterate through the rows
                for row in reader:
                    # Each row is a list of values, and you can access them by index
                    for index, value in enumerate(row):
                        num = value.split(':')[1].strip()
                        if index == 0:
                            start_frame = round(float(num))
                        else:
                            end_frame = round(float(num))
            print("Start frame ", start_frame, '\t', "End Frame ", end_frame)  # Print the values separated by tabs

            print("The difference between end and start:", end_frame - start_frame)
            # Join all elements except the last one with a comma separator
            new_dir_name = '_'.join(words[:-1])

            # Load the tab separated matrix file in Numpy
            matrix = np.loadtxt(directory + new_dir_name)

            # Save the matrix to a file
            print("Saving the complete matrix to a .npy file")
            np.save(directory + new_dir_name + '.npy', matrix)

            print("The original shape of the matrix is ", matrix.shape)
            # Slice only the columns, for example, columns 3 to 7
            sliced_matrix = matrix[:, start_frame:end_frame]

            print("The sliced matrix shape is ", sliced_matrix.shape)

            # Save the matrix to a file
            print("Saving the matrix to a .npy file")
            np.save(directory + new_dir_name + '_sliced' + '.npy', sliced_matrix)


def main():
    directory = "/Users/shrinivassampathmuthupalaniyappan/Desktop/Courses/Capstone/Local_Copy/Output/matrix/feed/"
    #save_matrix(directory)
    compare_matrix(directory, "M01_Session2_0020.npy")


if __name__ == '__main__':
    main()
