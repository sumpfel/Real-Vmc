import numpy as np
import csv

class AccelerometerCalibrator:
    acc_samples=[]
    def __init__(self):
        self.offsets = [0.0]*3

    def load(self,file):
        with open(file,'r') as f:
            rows = csv.reader(f)
            for row in rows:
                if row[0]=="acc":
                    self.offsets[0]=float(row[1])
                    self.offsets[1]=float(row[2])
                    self.offsets[2]=float(row[3])


    def store(self,file):
        rows = []
        with open(file,'r') as f:
            rows = list(csv.reader(f))

        x=0
        for row in rows:
            if row[0]=="acc":
                rows[x]=["acc"]+self.offsets
                break
            x+=1
        if x == len(rows):
            rows.append(["acc"]+self.offsets)

        with open(file,'w', newline="") as f:
            csv.writer(f).writerows(rows)

    def update_calibration(self, acc):
        self.acc_samples.append(acc)

    def calculate_offsets(self):

        if not self.acc_samples:
            raise ValueError("No samples collected for offset calculation. Call update_calibration first.")

        acc = [sum(x)/len(self.acc_samples) for x in zip(*self.acc_samples)]

        self.offsets[0] = -acc[0]
        self.offsets[1] = -acc[1]
        self.offsets[2] = -acc[2]

        x = acc.index(max(acc))
        self.offsets[x] = 9.81-acc[x]

    def apply_calibration(self, acc):
        if not self.offsets:
            raise ValueError("Calibration has not been calculated. Call calculate_offsets first.")

        # Use numpy to add offsets
        acc_np = np.array(acc)
        offsets_np = np.array(self.offsets)
        calibrated = acc_np + offsets_np

        return calibrated

    def print_calibration(self):
        print(f"Accelerometer Offsets: {self.offsets}")