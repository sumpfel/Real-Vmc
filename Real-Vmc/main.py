import usb
import usb.util
import time
import board
import busio
from adafruit_lsm6ds import LSM6DSOX
from adafruit_lis3mdl import LIS3MDL

from Real_VMC import calibrate_magnetometer
from Real_VMC import calibrate_gyro

def main():
    # Initialize I2C
    i2c = busio.I2C(board.SCL, board.SDA)

    # Initialize sensors
    try:
        lsm6dsox = LSM6DSOX(i2c, address=0x6B)  # LSM6DSOX detected at 0x6B
        print("LSM6DSOX initialized successfully.")
    except Exception as e:
        print(f"Error initializing LSM6DSOX: {e}")
        return

    try:
        lis3mdl = LIS3MDL(i2c, address=0x1E)  # LIS3MDL detected at 0x1E
        print("LIS3MDL initialized successfully.")
    except Exception as e:
        print(f"Error initializing LIS3MDL: {e}")
        return


    mag_calibrator=calibrate_magnetometer.magnetometer_calibrator()
    gyro_calibrator=calibrate_gyro.gyro_calibrator()

    try:
        while True:
            # Read data from LSM6DSOX
            accel = lsm6dsox.acceleration
            gyro = lsm6dsox.gyro

            # Read data from LIS3MDL
            magnetic = lis3mdl.magnetic

            # Print sensor readings
            #print(f"Acceleration (m/s^2): X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}")
            #print(f"Gyroscope (rad/s): X={gyro[0]:.2f}, Y={gyro[1]:.2f}, Z={gyro[2]:.2f}")
            #print(f"Magnetic Field (uT): X={magnetic[0]:.2f}, Y={magnetic[1]:.2f}, Z={magnetic[2]:.2f}")
            #print("-" * 50)

            mag_calibrator.update_calibration(magnetic)
            #mag_calibrator.print_min_max()
            gyro_calibrator.update_calibration(gyro)

            # Wait before next reading
            time.sleep(0.5)
    except KeyboardInterrupt:
        mag_calibrator.calculate_offsets()
        mag_calibrator.print_calibration()
        gyro_calibrator.calculate_bias()
        gyro_calibrator.calculate_noise()
        gyro_calibrator.print_calibration()
        print("Exiting program...")

if __name__ == "__main__":
    main()
