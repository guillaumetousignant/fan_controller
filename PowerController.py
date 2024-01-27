from RelayOutput import RelayOutput


class PowerController(object):
    enabled: bool = False

    def __init__(self, enabled: bool, relay: RelayOutput):
        self.enabled = enabled
        self.relay = relay

    def toggle(self) -> bool:
        self.enabled = not self.enabled
        if self.enabled:
            self.relay.turn_on()
        else:
            self.relay.turn_off()
        return True

    def turn_on(self):
        if not self.enabled:
            self.enabled = True
            self.relay.turn_on()
            return True
        return False

    def turn_off(self):
        if self.enabled:
            self.enabled = False
            self.relay.turn_off()
            return True
        return False
