import pigpio


class RelayOutput(object):
    relay_pin: int = 0

    def __init__(self, relay_pin: int, enabled: bool, pi: pigpio.pi):
        self.relay_pin = relay_pin
        self.pi = pi
        self.pi.set_mode(self.relay_pin, pigpio.OUTPUT)  # type: ignore
        self.pi.write(self.relay_pin, not enabled)  # type: ignore

    def turn_on(self):
        self.pi.write(self.relay_pin, False)  # type: ignore

    def turn_off(self):
        self.pi.write(self.relay_pin, True)  # type: ignore
