import numpy as np
from ahrs.filters import Madgwick
import time

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

def transform_axes(array, transform):
    result = np.zeros(4)
    axis_indices = {"x": 0, "y": 1, "z": 2, "w": 3}

    for old_axis, (new_axis, direction) in transform.items():
        result[axis_indices[new_axis]] = array[axis_indices[old_axis]] * direction

    result[3] = array[3]  # Keep w unchanged
    return result