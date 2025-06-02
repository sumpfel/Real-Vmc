import time
import board
import busio
from adafruit_lsm6ds import LSM6DSOX
from adafruit_lsm6ds import Rate as LSM6DSOX_Rate
from adafruit_lis3mdl import LIS3MDL
from adafruit_lis3mdl import Rate as LIS3MDL_Rate

from Real_VMC import calibrate_magnetometer, calibrate_gyro, calibrate_accelerometer

def main():
    i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)

    lsm6dsox = LSM6DSOX(i2c, address=0x6B)
    lsm6dsox.accelerometer_data_rate = LSM6DSOX_Rate.RATE_1_66K_HZ
    lsm6dsox.gyro_data_rate = LSM6DSOX_Rate.RATE_1_66K_HZ

    lis3mdl = LIS3MDL(i2c, address=0x1E)
    lis3mdl.data_rate = LIS3MDL_Rate.RATE_80_HZ


    mag_calibrator=calibrate_magnetometer.MagnetometerCalibrator()
    gyro_calibrator=calibrate_gyro.GyroCalibrator()
    acc_calibrator=calibrate_accelerometer.AccelerometerCalibrator()

    for i in range(100):
        acc_calibrator.update_calibration(lsm6dsox.acceleration)
        gyro_calibrator.update_calibration(lsm6dsox.gyro)
        time.sleep(0.1)

    acc_calibrator.calculate_offsets()
    acc_calibrator.print_calibration()
    acc_calibrator.store("sensor1.csv")

    gyro_calibrator.calculate_bias()
    gyro_calibrator.calculate_noise()
    gyro_calibrator.print_calibration()
    gyro_calibrator.store("sensor1.csv")

    print()
    input("Press enter to continue and start rotating sensor until the numbers stop changing\n\rexit with cntr-c")

    x=1
    try:
        while True:
            magnetic = lis3mdl.magnetic
            mag_calibrator.update_calibration(magnetic)
            if x%30==0:
                mag_calibrator.print_min_max()
            # time.sleep(.1)
            x+=1

    except KeyboardInterrupt:
        print()
        mag_calibrator.calculate_offsets()
        mag_calibrator.print_calibration()
        mag_calibrator.store("sensor1.csv")

        print("\n\rExiting program...")


if __name__ == "__main__":
    main()
