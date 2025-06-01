import numpy as np
import csv

class MagnetometerCalibrator():
    offsets = [0.0]*3
    scales = [0.0]*3

    def __init__(self):
        self.mag_min = [float('inf')] * 3
        self.mag_max = [float('-inf')] * 3

    def load(self,file):
        with open(file,'r') as f:
            rows = csv.reader(f)
            for row in rows:
                if row[0]=="mag":
                    self.offsets[0]=float(row[1])
                    self.offsets[1]=float(row[2])
                    self.offsets[2]=float(row[3])
                    self.scales[0]=float(row[4])
                    self.scales[1]=float(row[5])
                    self.scales[2]=float(row[6])

    def store(self, file):
        rows = []
        with open(file,'r') as f:
            rows = list(csv.reader(f))

        x=0
        for row in rows:
            if row[0]=="mag":
                rows[x]=["mag"]+self.offsets+self.scales
                break
            x+=1
        if x == len(rows):
            rows.append(["mag"]+self.offsets+self.scales)

        with open(file,'w', newline="") as f:
            csv.writer(f).writerows(rows)

    def update_calibration(self, mag):
        for i in range(3):
            self.mag_min[i] = min(self.mag_min[i], mag[i])
            self.mag_max[i] = max(self.mag_max[i], mag[i])

    def print_min_max(self):
        print(f"min: {self.mag_min}, max: {self.mag_max}")

    def calculate_offsets(self):
        if self.mag_max == float('-inf') or self.mag_min == float('inf'):
            raise ValueError("No samples collected for offset calculation. Call update_calibration first.")

        self.offsets = [(max_v + min_v) / 2 for max_v, min_v in zip(self.mag_max, self.mag_min)]
        self.scales = [(max_v - min_v) / 2 for max_v, min_v in zip(self.mag_max, self.mag_min)]

    def print_calibration(self):
        print(f"Magnetometer Offsets: {self.offsets}")
        print(f"Magnetometer Scales (half range): {self.scales}")

    def apply_calibration(self, mag):
        if self.offsets == [0.0]*3:
            raise ValueError("Calibration has not been calculated. Call calculate_offsets first.")

        mag_np = np.array(mag)
        offsets_np = np.array(self.offsets)
        scales_np = np.array(self.scales)

        calibrated_mag = (mag_np - offsets_np) / scales_np
        return calibrated_mag