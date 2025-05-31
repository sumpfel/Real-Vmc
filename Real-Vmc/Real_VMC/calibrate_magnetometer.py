class magnetometer_calibrator():
    offsets = []
    scales = []

    def __init__(self):
        self.mag_min = [float('inf')] * 3
        self.mag_max = [float('-inf')] * 3

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
        if not self.offsets or not self.scales:
            raise ValueError("Calibration has not been calculated. Call calculate_offsets first.")

        calibrated_mag = [(x-y)/z for x,y,z in zip(mag, self.offsets, self.scales)]
        return calibrated_mag