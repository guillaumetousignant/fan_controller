class FanController(object):
    enabled: bool = False
    duty_cycle: float = 0

    def __init__(self, enabled: bool, duty_cycle: float):
        self.enabled = enabled
        self.duty_cycle = duty_cycle

    def increase_duty_cycle(self, increment: float) -> bool:
        if self.duty_cycle < 100 and increment != 0:
            self.duty_cycle = min(self.duty_cycle + increment, 100)
            return True
        return False

    def decrease_duty_cycle(self, decrement: float) -> bool:
        if self.duty_cycle > 0 and decrement != 0:
            self.duty_cycle = max(self.duty_cycle - decrement, 0)
            return True
        return False

    def set_duty_cycle(self, duty_cycle: float) -> bool:
        new_duty_cycle = min(max(duty_cycle, 0), 100)
        if new_duty_cycle != self.duty_cycle:
            self.duty_cycle = new_duty_cycle
            return True
        return False
