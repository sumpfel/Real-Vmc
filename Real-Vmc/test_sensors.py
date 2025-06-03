import time
import board
import busio
from adafruit_lsm6ds import LSM6DSOX, Rate as LSM6DSOX_Rate
from adafruit_lsm6ds import AccelRange, GyroRange
from adafruit_lis3mdl import LIS3MDL, Rate as LIS3MDL_Rate, Range as LIS3MDL_Range

from Real_VMC import calibrate_magnetometer, calibrate_gyroscope, calibrate_accelerometer

def main():
    # Initialize I2C
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
    # Initialize sensors
    try:
        lsm6dsox = LSM6DSOX(i2c, address=0x6B)
        print("LSM6DSOX initialized successfully.")
        lsm6dsox.accelerometer_data_rate = LSM6DSOX_Rate.RATE_1_66K_HZ
        lsm6dsox.gyro_data_rate = LSM6DSOX_Rate.RATE_1_66K_HZ
        lsm6dsox.accelerometer_range = AccelRange.RANGE_2G
        lsm6dsox.gyroscope_range = GyroRange.RANGE_250_DPS
    except Exception as e:
        print(f"Error initializing LSM6DSOX: {e}")
        return

    try:
        lis3mdl = LIS3MDL(i2c, address=0x1E)
        print("LIS3MDL initialized successfully.")
        lis3mdl.data_rate = LIS3MDL_Rate.RATE_80_HZ
        lis3mdl.range = LIS3MDL_Range.RANGE_16_GAUSS
    except Exception as e:
        print(f"Error initializing LIS3MDL: {e}")
        return


    x=0
    print("start reading data")
    start_time=time.time()
    try:
        while True:

            # Read data from LIS3MDL
            magnetic = lis3mdl.magnetic

            # Read data from LSM6DSOX
            accel = lsm6dsox.acceleration
            gyro = lsm6dsox.gyro


            # Print sensor readings
            #print(f"Acceleration (m/s^2): X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}")
            #print(f"Gyroscope (rad/s): X={gyro[0]:.2f}, Y={gyro[1]:.2f}, Z={gyro[2]:.2f}")
            #print(f"Magnetic Field (uT): X={magnetic[0]:.2f}, Y={magnetic[1]:.2f}, Z={magnetic[2]:.2f}")
            #print("-" * 50)

            time.sleep(0.1)
            x+=1

    except KeyboardInterrupt:
        print("Exiting program...")
        elapsed_time = time.time()-start_time
        print(f"FPS: {x/elapsed_time:.2f} Duration: {elapsed_time:.2f}")


if __name__ == "__main__":
    main()
