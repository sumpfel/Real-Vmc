import usb
import usb.util
import time
import board
import busio
from adafruit_lsm6ds import LSM6DSOX
from adafruit_lsm6ds import Rate as LSM6DSOX_Rate
from adafruit_lis3mdl import LIS3MDL
from adafruit_lis3mdl import Rate as LIS3MDL_Rate

from Real_VMC import calibrate_magnetometer, calibrate_gyro, calibrate_accelerometer, sensor_fusion, visualizer

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
    gyro_calibrator=calibrate_gyro.GyroCalibrator()
    acc_calibrator=calibrate_accelerometer.AccelerometerCalibrator()

    mag_calibrator.load("sensor1.csv")
    gyro_calibrator.load("sensor1.csv")
    acc_calibrator.load("sensor1.csv")

    x=0
    sensor_fusing=sensor_fusion.SensorFusion()
    print("start reading data")
    start_time=time.time()
    try:
        while True:
            # Read data from LSM6DSOX
            accel = acc_calibrator.apply_calibration(lsm6dsox.acceleration)
            gyro = gyro_calibrator.apply_calibration(lsm6dsox.gyro)

            # Read data from LIS3MDL
            if x + 10 % 10==0:
                magnetic = lis3mdl.magnetic
                magnetic = mag_calibrator.apply_calibration(magnetic)
                q = sensor_fusing.update(gyro,accel,magnetic)
            else:
                q= sensor_fusing.update(gyro, accel)

            euler_angles = visualizer.quat_to_euler(q)
            print("Euler angles (degrees): Roll {:.2f}, Pitch {:.2f}, Yaw {:.2f}".format(*euler_angles))

            # Print sensor readings
            #print(f"Acceleration (m/s^2): X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}")
            #print(f"Gyroscope (rad/s): X={gyro[0]:.2f}, Y={gyro[1]:.2f}, Z={gyro[2]:.2f}")
            #print(f"Magnetic Field (uT): X={magnetic[0]:.2f}, Y={magnetic[1]:.2f}, Z={magnetic[2]:.2f}")
            #print("-" * 50)

            #time.sleep(0.1)
            x+=1

    except KeyboardInterrupt:
        print()
        mag_calibrator.print_calibration()
        gyro_calibrator.print_calibration()
        acc_calibrator.print_calibration()
        print("Exiting program...")
        elapsed_time = time.time()-start_time
        print(f"FPS: {x/elapsed_time:.2f} Duration: {elapsed_time:.2f}")


if __name__ == "__main__":
    main()
