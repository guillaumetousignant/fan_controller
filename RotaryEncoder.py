from enum import Enum, auto
from typing import Optional
from rich.progress import Progress, Task
from FanController import FanController
from PWMChannel import PWMChannel
from ProgressBar import ProgressBar
import pigpio


class RotaryEncoder(object):
    clk_pin: int = 0
    dt_pin: int = 0
    increment: float = 0
    fan: FanController = None
    pwm: PWMChannel = None
    progress_bar: Optional[ProgressBar] = None
    pi: pigpio.pi = None
    clk_callback: pigpio._callback = None
    dt_callback: pigpio._callback = None
    dt_status: bool = False
    clk_last_tick: int = 0
    dt_last_tick: int = 0
    DEBOUNCE_TICKS: int = 50

    def __init__(self, clk_pin: int, dt_pin: int, increment: float, fan: FanController, pwm: PWMChannel, progress_bar: Optional[ProgressBar], pi: pigpio.pi):
        self.clk_pin = clk_pin
        self.dt_pin = dt_pin
        self.increment = increment
        self.fan = fan
        self.pwm = pwm
        self.progress_bar = progress_bar
        self.pi = pi

        self.pi.set_mode(self.clk_pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.clk_pin, pigpio.PUD_UP)
        self.pi.set_mode(self.dt_pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.dt_pin, pigpio.PUD_UP)

        self.dt_status = self.pi.read(self.dt_pin)
        self.clk_last_tick = 0
        self.dt_last_tick = 0

        self.clk_callback = self.pi.callback(self.clk_pin, pigpio.RISING_EDGE, self.clk_callback_function)
        self.dt_callback = self.pi.callback(self.dt_pin, pigpio.EITHER_EDGE, self.dt_callback_function)

    def deactivate(self):
        self.clk_callback.cancel()
        self.dt_callback.cancel()

    def clk_callback_function(self, gpio: int, level: int, tick: int):
        if tick > self.clk_last_tick and (tick - self.clk_last_tick) > self.DEBOUNCE_TICKS:
            self.clk_last_tick = tick
            changed = self.fan.increase_duty_cycle(self.increment) if self.dt_status else self.fan.decrease_duty_cycle(self.increment)
            if changed:
                self.pwm.set_duty_cycle(self.fan.duty_cycle)
                if self.progress_bar is not None:
                    self.progress_bar.display_fan_speed(self.fan.duty_cycle)

    def dt_callback_function(self, gpio: int, level: int, tick: int):
        if tick > self.dt_last_tick and (tick - self.dt_last_tick) > self.DEBOUNCE_TICKS:
            self.dt_last_tick = tick
            if level == 0:
                self.dt_status = False
            elif level == 1:
                self.dt_status = True
