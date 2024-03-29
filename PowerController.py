from RelayOutput import RelayOutput
from typing import Callable


def do_nothing_bool(enabled: bool):
    pass


class PowerController(object):
    enabled: bool = False

    def __init__(self, enabled: bool, relay: RelayOutput):
        self.enabled = enabled
        self.relay = relay
        self.communicate_callback = do_nothing_bool

    def set_communicate_callback(self, communicate_callback: Callable[[bool], None]):
        self.communicate_callback = communicate_callback

    def communicate_power(self):
        self.communicate_callback(self.enabled)

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        if self.enabled:
            self.relay.turn_on()
        else:
            self.relay.turn_off()
        self.communicate_power()
        return True

    def turn_on(self):
        if not self.enabled:
            self.enabled = True
            self.relay.turn_on()
            self.communicate_power()
            return True
        self.communicate_power()
        return False

    def turn_off(self):
        if self.enabled:
            self.enabled = False
            self.relay.turn_off()
            self.communicate_power()
            return True
        self.communicate_power()
        return False
