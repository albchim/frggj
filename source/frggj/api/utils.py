# utils
import numpy as np


def invert_matrices_array(matrices_array):
    inverted_matrices = []
    for matrix in matrices_array:
        inverted_matrices.append(invert_matrix(matrix))
    return np.asarray(inverted_matrices).astype(float)


def invert_matrix(matrix):
    rotation_matrix = matrix[:3, :3]
    translation = matrix[:3, 3]
    inverted_matrix = np.eye(4)
    inverted_matrix[:3, :3] = rotation_matrix.T
    inverted_matrix[:3, 3] = -rotation_matrix.T @ translation
    return inverted_matrix
