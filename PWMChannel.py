import pigpio


class PWMChannel(object):
    pwm_pin: int = 0
    frequency: int = 0
    pi: pigpio.pi = None

    def __init__(self, pwm_pin: int, frequency: int, initial_duty: float, pi: pigpio.pi):
        self.pwm_pin = pwm_pin
        self.frequency = frequency
        self.pi = pi

        self.pi.hardware_PWM(self.pwm_pin, self.frequency, 10000 * initial_duty)

    def set_duty_cycle(self, duty_cycle: float):
        self.pi.hardware_PWM(self.pwm_pin, self.frequency, 10000 * duty_cycle)
