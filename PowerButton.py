from typing import Optional
from PowerController import PowerController
import pigpio


class PowerButton(object):
    button_pin: int = 0

    def __init__(self, button_pin: int, power: PowerController, pi: pigpio.pi):
        self.button_pin = button_pin
        self.power = power
        self.pi = pi
        self.pi.set_mode(self.button_pin, pigpio.INPUT)  # type: ignore
        self.pi.set_pull_up_down(self.button_pin, pigpio.PUD_UP)  # type: ignore

    def wait_for_release(self, timeout: Optional[int]) -> bool:
        if timeout is None:
            if self.pi.wait_for_edge(self.button_pin, pigpio.RISING_EDGE):  # type: ignore
                self.power.toggle()
                return True
            return False
        else:
            if self.pi.wait_for_edge(self.button_pin, pigpio.RISING_EDGE, timeout):  # type: ignore
                self.power.toggle()
                return True
            return False
