import board
import busio
import time

i2c = busio.I2C(board.SCL, board.SDA)

print("Scanning for I2C devices...")
while not i2c.try_lock():
    pass

try:
    devices = i2c.scan()
    if devices:
        print(f"Found I2C device(s) at: {[hex(address) for address in devices]}")
    else:
        print("No I2C devices found.")
finally:
    i2c.unlock()
