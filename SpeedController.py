from PWMChannel import PWMChannel
from ProgressBar import ProgressBar
from typing import Optional


class SpeedController(object):
    duty_cycle: float = 0
    progress_bar: Optional[ProgressBar] = None

    def __init__(self, duty_cycle: float, pwm: PWMChannel, progress_bar: Optional[ProgressBar]):
        self.duty_cycle = duty_cycle
        self.pwm = pwm
        self.progress_bar = progress_bar

    def apply_duty_cycle(self):
        self.pwm.set_duty_cycle(self.duty_cycle)
        if self.progress_bar is not None:
            self.progress_bar.display_fan_speed(self.duty_cycle)

    def increase_duty_cycle(self, increment: float) -> bool:
        if self.duty_cycle < 100 and increment != 0:
            self.duty_cycle = min(self.duty_cycle + increment, 100)
            self.apply_duty_cycle()
            return True
        return False

    def decrease_duty_cycle(self, decrement: float) -> bool:
        if self.duty_cycle > 0 and decrement != 0:
            self.duty_cycle = max(self.duty_cycle - decrement, 0)
            self.apply_duty_cycle()
            return True
        return False

    def set_duty_cycle(self, duty_cycle: float) -> bool:
        new_duty_cycle = min(max(duty_cycle, 0), 100)
        if new_duty_cycle != self.duty_cycle:
            self.duty_cycle = new_duty_cycle
            self.apply_duty_cycle()
            return True
        return False
