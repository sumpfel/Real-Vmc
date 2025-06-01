import numpy as np
from scipy.spatial.transform import Rotation as R

def quat_to_euler(q):
    w, x, y, z = q
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = np.arctan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if abs(sinp) >= 1:
        pitch = np.sign(sinp) * np.pi / 2  # use 90 degrees if out of range
    else:
        pitch = np.arcsin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = np.arctan2(siny_cosp, cosy_cosp)

    return np.rad2deg([roll, pitch, yaw])


def calculate_noise(q_list):
    if len(q_list) < 2:
        raise ValueError("The quaternion list must contain at least two quaternions.")

        # Use the first quaternion as the reference
    ref_quat = R.from_quat(q_list[0])

    angular_differences = []

    for quat in q_list[1:]:
        if not isinstance(quat, np.ndarray) or quat.shape != (4,):
            raise ValueError("Each quaternion must be a numpy array of shape (4,).")

        # Compute the relative rotation
        current_quat = R.from_quat(quat)
        relative_rotation = ref_quat.inv() * current_quat

        # Calculate the angle of the relative rotation in degrees
        angle = relative_rotation.magnitude() * (180 / np.pi)  # Convert radians to degrees
        angular_differences.append(angle)

    # Calculate mean and standard deviation
    mean_noise = np.mean(angular_differences)
    std_noise = np.std(angular_differences)

    return mean_noise, std_noise