import numpy as np
from ahrs.filters import Madgwick
import time
from scipy.spatial.transform import Rotation as R

class SensorFusion:
    def __init__(self):

        self.filter = Madgwick()
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.last_time = time.time()

        self.axes_names = ['x', 'y', 'z']

    def update(self, gyro, acc, mag=None):
        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time

        if delta_time > 0:  # Avoid division by zero
            self.filter.frequency = 1.0 / delta_time

        try:
            mag = mag / np.linalg.norm(mag)
            self.q = self.filter.updateMARG(self.q, gyr=gyro, acc=acc, mag=mag)
        except:
            self.q = self.filter.updateIMU(self.q, gyr=gyro, acc=acc)

        return self.q


class AbsoluteRotation:
    def __init__(self):
        # Initialize the absolute rotation quaternion
        self.q = np.array([1.0, 0.0, 0.0, 0.0])  # Identity quaternion

    def normalize_vector(self, vector):
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector

    def calculate_rotation(self, acc, mag):
        # Normalize accelerometer and magnetometer readings
        acc = self.normalize_vector(acc)
        mag = self.normalize_vector(mag)

        # Compute gravity direction from accelerometer (Z-axis)
        z_axis = acc

        # Compute east direction (X-axis) as cross product of mag and gravity
        east = np.cross(mag, z_axis)
        east = self.normalize_vector(east)

        # Compute north direction (Y-axis) as cross product of gravity and east
        north = np.cross(z_axis, east)

        # Construct rotation matrix from axes
        rotation_matrix = np.vstack([east, north, z_axis]).T

        # Convert rotation matrix to quaternion
        rotation = R.from_matrix(rotation_matrix)
        self.q = rotation.as_quat()

        return self.q

    def update(self, acc, mag):
        try:
            return self.calculate_rotation(acc, mag)
        except Exception as e:
            print(f"Error calculating rotation: {e}")
            return np.array([0.0]*4)

def transform_axes(array, transform):
    result = np.zeros(4)
    axis_indices = {"x": 0, "y": 1, "z": 2, "w": 3}

    for old_axis, (new_axis, direction) in transform.items():
        result[axis_indices[new_axis]] = array[axis_indices[old_axis]] * direction

    result[3] = array[3]  # Keep w unchanged
    return result