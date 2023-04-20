from typing import Optional
from FanController import FanController
import pigpio


class PowerButton(object):
    button_pin: int = 0
    relay_pin: int = 0
    fan: FanController = None
    pi: pigpio.pi = None

    def __init__(self, button_pin: int, relay_pin: int, fan: FanController, pi: pigpio.pi):
        self.button_pin = button_pin
        self.relay_pin = relay_pin
        self.fan = fan
        self.pi = pi
        self.pi.set_mode(self.button_pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.button_pin, pigpio.PUD_UP)
        self.pi.set_mode(self.relay_pin, pigpio.OUTPUT)
        self.pi.write(self.relay_pin, not self.fan.enabled)

    def switch(self):
        self.fan.enabled = not self.fan.enabled
        self.pi.write(self.relay_pin, not self.fan.enabled)

    def wait_for_release(self, timeout: Optional[int]) -> bool:
        if timeout is None:
            if self.pi.wait_for_edge(self.button_pin, pigpio.RISING_EDGE):
                self.switch()
                return True
            return False
        else:
            if self.pi.wait_for_edge(self.button_pin, pigpio.RISING_EDGE, timeout):
                self.switch()
                return True
            return False
