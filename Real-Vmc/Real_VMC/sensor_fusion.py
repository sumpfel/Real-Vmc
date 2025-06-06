import numpy as np
import math
import time
from scipy.spatial.transform import Rotation

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
        rotation = Rotation.from_matrix(rotation_matrix)
        self.q = rotation.as_quat()

        return self.q


    def update(self, acc, mag):
        try:
            return self.calculate_rotation(acc, mag)
        except Exception as e:
            print(f"Error calculating rotation: {e}")
            return np.array([0.0]*4)

class SimpleFusion():
    def __init__(self,roll=0.0,pitch=0.0,yaw=0.0,smooth=10):
        self.rotation=np.array([roll,pitch,yaw],dtype=float) #roll pitch yaw
        self.last_update = time.time()
        self.acc_readings=[]
        self.smooth=smooth

    def update(self, acc=None ,gyro=None, mag=None):
        elapsed = time.time()-self.last_update
        self.last_update = time.time()


        if gyro is not None:
            gyro = np.array(gyro)
            self.rotation = self.rotation+gyro*elapsed
            if acc is not None:
                acc=np.array(acc)
                if self.smooth>0:
                    self.acc_readings.append(acc)
                    acc = smooth_rotation(self.acc_readings, self.smooth)

                acc_n=acc/np.linalg.norm(acc)
                roll=math.atan2(acc_n[1],acc_n[2])
                pitch=math.atan2(-acc_n[0],math.sqrt(acc_n[1]**2+acc_n[2]**2))

                self.rotation[:2] = (self.rotation[:2]+np.array([roll,pitch]))/2

        elif acc is not None:
            acc = np.array(acc)

            if self.smooth > 0:
                self.acc_readings.append(acc)
                acc = smooth_rotation(self.acc_readings, self.smooth)

            acc_n = acc/np.linalg.norm(acc)
            #print("acc:",acc_n)
            self.rotation[0] = math.atan2(acc_n[1], acc_n[2])
            self.rotation[1] = math.atan2(-acc_n[0], math.sqrt(acc_n[1] ** 2 + acc_n[2] ** 2))
            #print("rot:",self.rotation)

        if mag is not None:
            mag= np.array(mag)
            pitch = self.rotation[1]
            roll = self.rotation[0]

            mag = mag / np.linalg.norm(mag)

            mag_x = mag[0] * math.cos(pitch) + mag[2] * math.sin(pitch)
            mag_y = mag[0] * math.sin(pitch) * math.sin(roll) + mag[1] * math.cos(roll) - mag[2] * math.cos(pitch) * math.sin(roll)

            self.rotation[2] = math.atan2(mag_y, mag_x)

        return self.rotation



def transform_axes(array, transform):
    result = np.zeros(4)
    axis_indices = {"x": 0, "y": 1, "z": 2, "w": 3}

    for old_axis, (new_axis, direction) in transform.items():
        result[axis_indices[new_axis]] = array[axis_indices[old_axis]] * direction

    result[3] = array[3]  # Keep w unchanged
    return result

def smooth_rotation(q_list,amount):
    x = len(q_list)
    if amount > x:
        return q_list[x-1]

    qs = np.array(q_list[-amount:])
    return np.mean(qs, axis=0)

