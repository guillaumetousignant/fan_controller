import pigpio


class PWMChannel(object):
    pwm_pin: int = 0
    frequency: int = 0
    min_duty: float = 0
    max_duty: float = 100

    def get_duty(self, duty_cycle: float) ->int:
        return int(duty_cycle/100 * (self.max_duty - self.min_duty) + self.min_duty)

    def __init__(self, pwm_pin: int, frequency: int, min_duty: float, max_duty: float, initial_duty: float, pi: pigpio.pi):
        self.pwm_pin = pwm_pin
        self.frequency = frequency
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.pi = pi

        self.pi.hardware_PWM(self.pwm_pin, self.frequency, 10000 * self.get_duty(initial_duty))  # type: ignore

    def set_duty_cycle(self, duty_cycle: float):
        self.pi.hardware_PWM(self.pwm_pin, self.frequency, 10000 * self.get_duty(duty_cycle))  # type: ignore
