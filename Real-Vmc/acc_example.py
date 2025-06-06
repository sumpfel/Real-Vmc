from Real_VMC import calibrate_accelerometer, sensor_fusion
import time
import numpy as np

#this is only if using adafruit lsm6sdox replace lsm6dsox.acceleration with [x, y, z] readings of your sensor otherwise
from adafruit_lsm6ds import LSM6DSOX
import board
import busio
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
lsm6dsox = LSM6DSOX(i2c, address=0x6B)


def calibrate():
    acc_calibrator=calibrate_accelerometer.AccelerometerCalibrator()

    for i in range(200):
        acc_calibrator.update_calibration(lsm6dsox.acceleration)
        time.sleep(0.1)

    acc_calibrator.calculate_offsets()
    acc_calibrator.print_calibration()
    acc_calibrator.store("sensor2csv")

def update():
    acc_calibrator=calibrate_accelerometer.AccelerometerCalibrator()
    acc_calibrator.load("sensor2.csv")

    sensor_fusing = sensor_fusion.SimpleFusion()

    while True:
        acc = acc_calibrator.apply_calibration(lsm6dsox.acceleration)
        euler=sensor_fusing.update(acc)
        angles = np.rad2deg(euler)
        print(f"Roll: {angles[0]:8.2f}°, Pitch: {angles[1]:8.2f}°, Yaw: {angles[2]:8.2f}°")

if __name__=="__main__":
    update()