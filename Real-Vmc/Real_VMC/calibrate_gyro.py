class gyro_calibrator:
    def __init__(self):
        self.gyro_bias = [0.0] * 3
        self.gyro_noise = [0.0] * 3
        self.bias_samples = []

    def update_calibration(self, gyro):
        self.bias_samples.append(gyro)

    def calculate_bias(self):
        if not self.bias_samples:
            print("No samples collected for bias calculation.")
            return

        num_samples = len(self.bias_samples)
        self.gyro_bias = [
            sum(sample[i] for sample in self.bias_samples) / num_samples
            for i in range(3)
        ]

    def calculate_noise(self):
        if not self.bias_samples:
            print("No samples collected for noise calculation.")
            return

        num_samples = len(self.bias_samples)
        means = self.gyro_bias
        self.gyro_noise = [
            (sum((sample[i] - means[i])**2 for sample in self.bias_samples) / num_samples) ** 0.5
            for i in range(3)
        ]

    def print_calibration(self):
        print(f"Noise: {self.gyro_noise}")
        print(f"Bias: {self.gyro_bias}")

    def clear_samples(self):
        self.bias_samples = []
        print("Sample data cleared.")