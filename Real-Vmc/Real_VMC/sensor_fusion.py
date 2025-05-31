import numpy as np
from ahrs.filters import Madgwick

class SensorFusion:
    def __init__(self, sample_rate=10, dof=9):
        assert dof in (6, 9), "DOF must be 6 or 9"

        self.sample_rate = sample_rate
        self.dof = dof

        self.filter = Madgwick(frequency=sample_rate)
        self.q = np.array([1.0, 0.0, 0.0, 0.0])

    def update(self, gyro, acc, mag=None):
        match self.dof:
            case 6:
                self.q = self.filter.updateIMU(self.q, gyr=gyro, acc=acc)
            case 9:
                if mag is None:
                    raise ValueError("Magnetometer data required for 9 DoF mode")
                self.q = self.filter.updateMARG(self.q, gyr=gyro, acc=acc, mag=mag)

        return self.q
