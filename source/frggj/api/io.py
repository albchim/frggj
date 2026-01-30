import json
import numpy as np
import pygame as pg
from frggj.api.utils import invert_matrices_array


def import_mesh(filepath):
    with open(filepath) as json_data:
        data = json.load(json_data)
        json_data.close()
        points_list = []
        for point in data["points"]:
            points_list.append([point[0], point[1], point[2], 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        points = np.asarray(points_list).astype(float)
        
        triangles_list = []
        for triangle in data["triangles"]:
            triangles_list.append([triangle[0], triangle[1], triangle[2]])
        triangles = np.asarray(triangles_list).astype(int)

        uvs_list = []
        for uv in data["uvs"]:
            uvs_list.append([[uv[0], 1.0-uv[1]], [uv[2], 1.0-uv[3]], [uv[4], 1.0-uv[5]]])
        uvs = np.asarray(uvs_list).astype(float)
        return points, triangles,uvs


def import_texture(filepath):
    texture = pg.surfarray.array3d(pg.image.load(filepath))
    return texture


def import_skeleton(filepath):
    with open(filepath) as json_data:
        data = json.load(json_data)
        json_data.close()
        binding_indices = np.asarray(data["binding_indices"]).astype(int)
        binding_matrices = np.asarray(data["binding_matrices"]).astype(float)
        binding_matrices = invert_matrices_array(binding_matrices)
        return binding_indices, binding_matrices


def import_animation(filepath):
    with open(filepath) as json_data:
        data = json.load(json_data)
        json_data.close()
        frames_data = np.asarray(data["frames"]).astype(float)
        return data["fps"], data["length"], frames_data


def import_takes(filepath):
    with open(filepath) as json_data:
        data = json.load(json_data)
        json_data.close()
        return data
