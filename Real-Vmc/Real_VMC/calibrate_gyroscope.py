import numpy as np
import csv

class GyroCalibrator:
    def __init__(self):
        self.gyro_bias = [0.0] * 3
        self.gyro_noise = [0.0] * 3
        self.bias_samples = []

    def load(self,file):
        with open(file,'r') as f:
            rows = csv.reader(f)
            for row in rows:
                if row[0]=="gyro":
                    self.gyro_bias[0]=float(row[1])
                    self.gyro_bias[1]=float(row[2])
                    self.gyro_bias[2]=float(row[3])
                    self.gyro_bias[0]=float(row[4])
                    self.gyro_noise[1]=float(row[5])
                    self.gyro_noise[2]=float(row[6])

    def store(self,file):
        rows = []
        with open(file,'r') as f:
            rows = list(csv.reader(f))

        x=0
        for row in rows:
            if row[0]=="gyro":
                rows[x]=["gyro"]+self.gyro_bias+self.gyro_noise
                break
            x+=1
        if x == len(rows):
            rows.append(["gyro"]+self.gyro_bias+self.gyro_noise)

        with open(file,'w', newline="") as f:
            csv.writer(f).writerows(rows)

    def update_calibration(self, gyro):
        self.bias_samples.append(gyro)

    def calculate_bias(self):
        if not self.bias_samples:
            raise ValueError("No samples collected for bias calculation. Call update_calibration first.")

        num_samples = len(self.bias_samples)
        self.gyro_bias = [
            sum(sample[i] for sample in self.bias_samples) / num_samples
            for i in range(3)
        ]

    def calculate_noise(self):
        if not self.bias_samples:
            raise ValueError("No samples collected for noise calculation. Call update_calibration first.")

        num_samples = len(self.bias_samples)
        means = self.gyro_bias
        self.gyro_noise = [
            (sum((sample[i] - means[i])**2 for sample in self.bias_samples) / num_samples) ** 0.5
            for i in range(3)
        ]

    def print_calibration(self):
        print(f"Gyroscope Noise: {self.gyro_noise}")
        print(f"Gyroscope Bias: {self.gyro_bias}")

    def clear_samples(self):
        self.bias_samples = []
        print("Sample data cleared.")

    def apply_calibration(self, acc):
        if not self.gyro_bias:
            raise ValueError("Calibration has not been calculated. Call calculate_bias first.")

        acc_np = np.array(acc)
        bias_np = np.array(self.gyro_bias)

        calibrated = acc_np - bias_np
        return calibrated