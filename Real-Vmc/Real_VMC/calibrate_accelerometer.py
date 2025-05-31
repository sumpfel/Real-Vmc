class accelerometer_calibrator:
    acc_samples=[]
    def __init__(self):
        self.offsets = [0.0]*3

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
            raise ValueError("Calibration has not been calculated. Call calculate_accelerometer first.")

        return [x + y for x, y in zip(acc, self.offsets)]

    def print_calibration(self):
        print(f"Accelerometer Offsets: {self.offsets}")