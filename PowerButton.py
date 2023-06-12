from typing import Optional
from FanController import FanController
import pigpio


class PowerButton(object):
    button_pin: int = 0
    relay_pin: int = 0

    def __init__(self, button_pin: int, relay_pin: int, fan: FanController, pi: pigpio.pi):
        self.button_pin = button_pin
        self.relay_pin = relay_pin
        self.fan = fan
        self.pi = pi
        self.pi.set_mode(self.button_pin, pigpio.INPUT)  # type: ignore
        self.pi.set_pull_up_down(self.button_pin, pigpio.PUD_UP)  # type: ignore
        self.pi.set_mode(self.relay_pin, pigpio.OUTPUT)  # type: ignore
        self.pi.write(self.relay_pin, not self.fan.enabled)  # type: ignore

    def switch(self):
        self.fan.enabled = not self.fan.enabled
        self.pi.write(self.relay_pin, not self.fan.enabled)  # type: ignore

    def switch_on(self):
        if not self.fan.enabled:
            self.fan.enabled = True
            self.pi.write(self.relay_pin, True)

    def switch_off(self):
        if self.fan.enabled:
            self.fan.enabled = False
            self.pi.write(self.relay_pin, False)

    def wait_for_release(self, timeout: Optional[int]) -> bool:
        if timeout is None:
            if self.pi.wait_for_edge(self.button_pin, pigpio.RISING_EDGE):  # type: ignore
                self.switch()
                return True
            return False
        else:
            if self.pi.wait_for_edge(self.button_pin, pigpio.RISING_EDGE, timeout):  # type: ignore
                self.switch()
                return True
            return False
