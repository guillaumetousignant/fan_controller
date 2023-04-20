class FanController(object):
    enabled: bool = False
    duty_cycle: float = 0
    min_duty: float = 0
    max_duty: float = 100

    def __init__(self, enabled: bool, min_duty: float, max_duty: float, duty_cycle: float):
        self.enabled = enabled
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.duty_cycle = duty_cycle

    def increase_duty_cycle(self, increment: float) -> bool:
        if self.duty_cycle < self.max_duty and increment != 0:
            self.duty_cycle = min(self.duty_cycle + increment, self.max_duty)
            return True
        return False

    def decrease_duty_cycle(self, decrement: float) -> bool:
        if self.duty_cycle > self.min_duty and decrement != 0:
            self.duty_cycle = max(self.duty_cycle - decrement, self.min_duty)
            return True
        return False

    def set_duty_cycle(self, duty_cycle: float) -> bool:
        new_duty_cycle = min(max(duty_cycle, self.min_duty), self.max_duty)
        if new_duty_cycle != self.duty_cycle:
            self.duty_cycle = new_duty_cycle
            return True
        return False
