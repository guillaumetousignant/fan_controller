from SpeedController import SpeedController
import pigpio


class RotaryEncoder(object):
    clk_pin: int = 0
    dt_pin: int = 0
    increment: float = 0
    dt_status: bool = False
    clk_last_tick: int = 0
    dt_last_tick: int = 0
    DEBOUNCE_TICKS: int = 50

    def __init__(self, clk_pin: int, dt_pin: int, increment: float, speed: SpeedController, pi: pigpio.pi):
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.increment = increment
        self.speed = speed
        self.pi = pi

        self.pi.set_mode(self.clk_pin, pigpio.INPUT)  # type: ignore
        self.pi.set_pull_up_down(self.clk_pin, pigpio.PUD_UP)  # type: ignore
        self.pi.set_mode(self.dt_pin, pigpio.INPUT)  # type: ignore
        self.pi.set_pull_up_down(self.dt_pin, pigpio.PUD_UP)  # type: ignore

        self.dt_status = self.pi.read(self.dt_pin)  # type: ignore
        self.clk_last_tick = 0
        self.dt_last_tick = 0

        self.clk_callback = self.pi.callback(self.clk_pin, pigpio.RISING_EDGE, self.clk_callback_function)  # type: ignore
        self.dt_callback = self.pi.callback(self.dt_pin, pigpio.EITHER_EDGE, self.dt_callback_function)  # type: ignore

    def deactivate(self):
        self.clk_callback.cancel()  # type: ignore
        self.dt_callback.cancel()  # type: ignore

    def clk_callback_function(self, gpio: int, level: int, tick: int):
        if tick > self.clk_last_tick and (tick - self.clk_last_tick) > self.DEBOUNCE_TICKS:
            self.clk_last_tick = tick
            self.speed.increase_duty_cycle(self.increment) if self.dt_status else self.speed.decrease_duty_cycle(self.increment)

    def dt_callback_function(self, gpio: int, level: int, tick: int):
        if tick > self.dt_last_tick and (tick - self.dt_last_tick) > self.DEBOUNCE_TICKS:
            self.dt_last_tick = tick
            if level == 0:
                self.dt_status = False
            elif level == 1:
                self.dt_status = True
