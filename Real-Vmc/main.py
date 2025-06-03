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

    mag_calibrator.load("sensor1.csv")
    gyro_calibrator.load("sensor1.csv")
    acc_calibrator.load("sensor1.csv")

    global mag_, gyro_, acc_, mag, gyro, acc

    mag = [0.0, 0.0, 0.0]
    gyro = [0.0, 0.0, 0.0]
    acc = [0.0, 0.0, 0.0]

    # Locks for thread synchronization
    acc_lock = threading.Lock()
    gyro_lock = threading.Lock()
    mag_lock = threading.Lock()

    # Thread functions
    def read_sensors():
        global acc,mag,gyro
        while True:
            with acc_lock:
                acc = acc_calibrator.apply_calibration(lsm6dsox.acceleration)
                #gyro = gyro_calibrator.apply_calibration(lsm6dsox.gyro)
                mag = mag_calibrator.apply_calibration(lis3mdl.magnetic)

    # Start threads
    thread_r_a = threading.Thread(target=read_sensors, daemon=True)
    thread_r_a.start()


    change_axes={
    "x": ("x", 1),
    "y": ("z", 1),
    "z": ("y", 1)
}

    exclude_bones = ['RightLowerArm', 'RightUpperArm', 'RightHand']
    exclude_blendshapes =[] #['Blink', 'Smile']
    forwarder = vmc_connection.VMCForwarder(exclude_bones=exclude_bones, exclude_blendshapes=exclude_blendshapes)

    def run_forwarder():
        forwarder.start()

    forwarder_thread = threading.Thread(target=run_forwarder, daemon=True)
    forwarder_thread.start()


    x=0
    sensor_fusing=sensor_fusion.AbsoluteRotation()
    print("start reading data")
    start_time=time.time()
    q_list=[]
    q=np.array([1.0, 0.0, 0.0, 0.0])
    try:
        while True:
            q = sensor_fusing.update(acc, mag)

            q = sensor_fusion.transform_axes(q,change_axes)
            #q_list.append(np.copy(q))
            forwarder.send_bone_rotation("RightUpperArm",q)
            #visualizer.print_rotation_in_degrees(q)
            #print(f"gyro: {np.round(gyro, 1)}, acc: {np.round(acc, 1)}, mag: {np.round(mag, 1)}")
            angles=visualizer.quat_to_euler(q)
            print(f"Roll: {angles[0]:8.2f}°, Pitch: {angles[1]:8.2f}°, Yaw: {angles[2]:8.2f}°")
            x += 1
            #time.sleep(.5)

    except KeyboardInterrupt:
        forwarder.shutdown()
        print("\n\rcalibration:")
        mag_calibrator.print_calibration()
        gyro_calibrator.print_calibration()
        acc_calibrator.print_calibration()
        print("\n\rnoise:")
        noise=visualizer.calculate_noise(q_list)
        print("Mean Noise (deg):", noise[0])
        print("Std Noise (deg):", noise[1])

        print("Exiting program...")
        elapsed_time = time.time()-start_time
        print(f"FPS: {x/elapsed_time:.2f} Duration: {elapsed_time:.2f}")


if __name__ == "__main__":
    main()
