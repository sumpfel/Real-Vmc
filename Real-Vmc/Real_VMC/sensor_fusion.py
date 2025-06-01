import numpy as np
from ahrs.filters import Madgwick
import time

class SensorFusion:
    def __init__(self):

        self.filter = Madgwick()
        self.q = np.array([1.0, 0.0, 0.0, 0.0])
        self.last_time = time.time()

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
