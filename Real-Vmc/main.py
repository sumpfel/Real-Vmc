import usb
import usb.util
import time
import board
import busio
import numpy as np
from adafruit_lsm6ds import LSM6DSOX
from adafruit_lsm6ds import Rate as LSM6DSOX_Rate
from adafruit_lis3mdl import LIS3MDL
from adafruit_lis3mdl import Rate as LIS3MDL_Rate
import threading

from Real_VMC import calibrate_magnetometer, calibrate_gyroscope, calibrate_accelerometer, sensor_fusion, visualizer,vmc_connection

def main():
    # Initialize I2C
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
    # Initialize sensors
    try:
        lsm6dsox = LSM6DSOX(i2c, address=0x6B)
        print("LSM6DSOX initialized successfully.")
        lsm6dsox.accelerometer_data_rate = LSM6DSOX_Rate.RATE_1_66K_HZ
        lsm6dsox.gyro_data_rate = LSM6DSOX_Rate.RATE_1_66K_HZ
    except Exception as e:
        print(f"Error initializing LSM6DSOX: {e}")

        return

    try:
        lis3mdl = LIS3MDL(i2c, address=0x1E)
        print("LIS3MDL initialized successfully.")
        lis3mdl.data_rate = LIS3MDL_Rate.RATE_80_HZ
    except Exception as e:
        print(f"Error initializing LIS3MDL: {e}")
        return


    mag_calibrator=calibrate_magnetometer.MagnetometerCalibrator()
    gyro_calibrator=calibrate_gyroscope.GyroCalibrator()
    acc_calibrator=calibrate_accelerometer.AccelerometerCalibrator()

    calibration_file = "sensor2.csv"

    mag_calibrator.load(calibration_file)
    gyro_calibrator.load(calibration_file)
    acc_calibrator.load(calibration_file)

    global mag_, gyro_, acc_, mag, gyro, acc

    mag_ = [0.0, 0.0, 0.0]
    gyro_ = [0.0, 0.0, 0.0]
    acc_ = [0.0, 0.0, 0.0]

    mag = [0.0, 0.0, 0.0]
    gyro = [0.0, 0.0, 0.0]
    acc = [0.0, 0.0, 0.0]


    # def read_sensors():
    #     global acc_, mag_, gyro_
    #     print("start reading sensors...")
    #     while True:
    #         acc_ = lsm6dsox.acceleration
    #         #gyro_ = lsm6dsox.gyro
    #         mag_ = lis3mdl.magnetic
    #
    # def calibrate_sensors():
    #     global mag_, gyro_, acc_, mag, gyro, acc
    #     print("start calibrating sensors...")
    #     while True:
    #         acc = acc_calibrator.apply_calibration(acc_)
    #         mag = mag_calibrator.apply_calibration(mag_)
    #         #gyro = gyro_calibrator.apply_calibration(gyro_)

    # thread_c_s = threading.Thread(target=calibrate_sensors, daemon=True)
    # thread_c_s.start()

    def read_sensors():
        global acc, mag, gyro
        print("start reading & calibrating sensors...")
        while True:
            acc = acc_calibrator.apply_calibration(lsm6dsox.acceleration)
            gyro = gyro_calibrator.apply_calibration(lsm6dsox.gyro)
            mag = mag_calibrator.apply_calibration(lis3mdl.magnetic)

    thread_r_s = threading.Thread(target=read_sensors, daemon=True)
    thread_r_s.start()


    change_axes = {
        "x": ("x", 1),
        "y": ("z", 1),
        "z": ("y", -1)
    }

    exclude_bones = ["Head"]#['RightLowerArm', 'RightUpperArm', 'RightHand',"LeftUpperLeg","LeftLowerLeg"]
    exclude_blendshapes =[] #['Blink', 'Smile']
    forwarder = vmc_connection.VMCForwarder(exclude_bones=exclude_bones, exclude_blendshapes=exclude_blendshapes)

    def run_forwarder():
        forwarder.start()

    forwarder_thread = threading.Thread(target=run_forwarder, daemon=True)
    forwarder_thread.start()


    sensor_fusing=sensor_fusion.SimpleFusion(smooth=0)
    #q=np.array([1.0, 0.0, 0.0, 0.0])
    #q_list=[]
    loop_count = 0

    time.sleep(1)

    print("start sending...")

    start_time=time.time()
    try:
        while True:
            loop_count += 1
            e = sensor_fusing.update(acc,gyro,mag)
            #q = sensor_fusion.transform_axes(q,change_axes)
            #q_list.append(np.copy(q))
            #q = sensor_fusion.smooth_rotation(q_list,500)
            #print("q:",q)

            #forwarder.send_bone_rotation("Head",q)
            #print(f"gyro: {np.round(gyro, 1)}, acc: {np.round(acc, 1)}, mag: {np.round(mag, 1)}")
            #angles=visualizer.quat_to_euler(q)
            angles=np.rad2deg(e)
            print(f"Roll: {angles[0]:8.2f}°, Pitch: {angles[1]:8.2f}°, Yaw: {angles[2]:8.2f}°")

    except KeyboardInterrupt:
        forwarder.shutdown()

        print("\n\rcalibration:")
        mag_calibrator.print_calibration()
        gyro_calibrator.print_calibration()
        acc_calibrator.print_calibration()

        #print("\n\rnoise:") #if not rotating sensor this should be as close to 0 as possible if not calibrate your sensors.
        #noise=visualizer.calculate_noise(q_list)
        #print("Mean Noise (deg):", noise[0])
        #print("Std Noise (deg):", noise[1])

        print("\n\rExiting program...")
        elapsed_time = time.time()-start_time
        print(f"VMC Messages sent/s: {loop_count/elapsed_time:.2f} Duration: {elapsed_time:.2f}")


if __name__ == "__main__":
    main()
