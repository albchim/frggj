# transform
import numpy as np
from frggj.api.utils import invert_matrix


class GTransform(object):
    def __init__(self):
        self._matrix = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
        self._constraint = None
        self._constraint_offset = None

    def set_translation(self, translation):
        self._matrix[0][3] = translation[0]
        self._matrix[1][3] = translation[1]
        self._matrix[2][3] = translation[2]

    def get_translation(self, four=False):
        if four:
            return np.asarray([self._matrix[0][3], self._matrix[1][3], self._matrix[2][3], 1.0])
        else:
            return np.asarray([self._matrix[0][3], self._matrix[1][3], self._matrix[2][3]])

    def get_eulers(self):
        """
        Extract (yaw, pitch, roll) from a 4x4 transform matrix assuming:
            R = Ry(yaw) @ Rx(pitch) @ Rz(roll)
        where yaw is about +Y (up), pitch about +X, roll about +Z.

        Returns: (yaw, pitch, roll) in radians by default (degrees if degrees=True).
        """
        R = self._matrix[:3, :3]

        # Clamp for numerical stability
        r23 = float(R[1, 2])
        r23 = max(-1.0, min(1.0, r23))

        # From derived relationships:
        # R[1,2] = -sin(pitch)
        pitch = -np.arcsin(r23)
        c_pitch = np.cos(pitch)

        # Gimbal lock when cos(pitch) ~ 0
        eps = 1e-8
        if abs(c_pitch) > eps:
            # roll from: R[1,0] = cos(pitch)*sin(roll), R[1,1] = cos(pitch)*cos(roll)
            roll = np.arctan2(R[1, 0], R[1, 1])

            # yaw from: R[0,2] = sin(yaw)*cos(pitch), R[2,2] = cos(yaw)*cos(pitch)
            yaw = np.arctan2(R[0, 2], R[2, 2])
        else:
            # Gimbal lock: choose roll = 0 and solve yaw from remaining terms
            roll = 0.0
            yaw = np.arctan2(-R[2, 0], R[0, 0])

        return np.degrees([pitch, yaw, roll])
        
    def set_eulers(self, angles):
        x = np.deg2rad(angles[0])
        y = np.deg2rad(angles[1])
        z = np.deg2rad(angles[2])

        cx, sx = np.cos(x), np.sin(x)
        cy, sy = np.cos(y), np.sin(y)
        cz, sz = np.cos(z), np.sin(z)

        Rx = np.array([
            [1,  0,   0],
            [0, cx, -sx],
            [0, sx,  cx]
        ])

        Ry = np.array([
            [ cy, 0, sy],
            [  0, 1,  0],
            [-sy, 0, cy]
        ])

        Rz = np.array([
            [cz, -sz, 0],
            [sz,  cz, 0],
            [ 0,   0, 1]
        ])

        R = Ry @ Rx @ Rz

        self._matrix[:3, :3] = R

    def get_front(self):
        return np.asarray([self._matrix[0][2], self._matrix[1][2], self._matrix[2][2]])

    def get_side(self):
        return np.asarray([self._matrix[0][0], self._matrix[1][0], self._matrix[2][0]])

    def get_matrix(self):
        return self._matrix

    def set_matrix(self, matrix):
        self._matrix = matrix

    def set(self, row, col, value):
        self._matrix[row][col] = value

    def get(self, row, col):
        return self._matrix[row][col]

    def get_inverted(self):
        return np.asarray([
            [self._matrix[0, 0], self._matrix[1, 0], self._matrix[2, 0], -self._matrix[0, 3]],
            [self._matrix[0, 1], self._matrix[1, 1], self._matrix[2, 1], -self._matrix[1, 3]],
            [self._matrix[0, 2], self._matrix[1, 2], self._matrix[2, 2], -self._matrix[2, 3]],
            [0.0, 0.0, 0.0, 1.0]
        ])

    def set_parent_constraint(self, transform):
        self._constraint = transform
        self._constraint_offset = GTransform()
        self._constraint_offset.set_matrix(invert_matrix(transform.get_matrix()) @ self.get_matrix())

    def get_matrix_parent_constrained(self):
        return self._constraint.get_matrix() @ self._constraint_offset.get_matrix()
    
    def get_matrix_constrained(self):
        point_constraint = GTransform()
        point_constraint.set_translation(self._constraint.get_translation())
        return point_constraint.get_matrix() @ self._constraint_offset.get_matrix()
