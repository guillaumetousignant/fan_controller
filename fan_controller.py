#!/usr/bin/env python3

import sys
import argparse
from RotaryEncoder import RotaryEncoder
from FanDisplay import FanDisplay
from PowerButton import PowerButton
from FanController import FanController
from PWMChannel import PWMChannel
from ProgressBar import ProgressBar
import pigpio
from pathlib import Path


def init_gpio(silent: bool) -> pigpio.pi:
    return pigpio.pi()


def fan_controller(
    max_duty: float, min_duty: float, frequency: int, refresh: float, increment: float, font_path: Path, verbose: bool, silent: bool, graphical: bool
):
    PWM_PIN = 12
    BUTTON_PIN = 4
    RELAY_PIN = 6
    CLK_PIN = 16
    DT_PIN = 26

    pi = init_gpio(silent)

    fan = FanController(False, min_duty, max_duty, max_duty)
    progress_bar = None if not graphical else ProgressBar()
    if progress_bar is not None:
        progress_bar.display_fan_speed(fan.duty_cycle)
    pwm = PWMChannel(PWM_PIN, frequency, fan.duty_cycle, pi)
    button = PowerButton(BUTTON_PIN, RELAY_PIN, fan, pi)
    encoder = RotaryEncoder(CLK_PIN, DT_PIN, increment, fan, pwm, progress_bar, pi)
    display = FanDisplay(refresh, font_path, fan)

    if verbose:
        print("System initialised")

    try:
        while True:
            button.wait_for_release(500)
    except KeyboardInterrupt:
        if verbose:
            print("Keyboard interrupt received")
    finally:
        if verbose:
            print("Cleaning up")
        if fan.enabled:
            button.switch()
        display.stop()
        encoder.deactivate()
        pi.stop()  # type: ignore


def main(argv: list[str]):
    parser = argparse.ArgumentParser(prog="Fan Controller", description="Controls fans")
    parser.add_argument("-m", "--max", type=float, default=100, help="maximum duty cycle")
    parser.add_argument("-n", "--min", type=float, default=20, help="minimum duty cycle")
    parser.add_argument("-e", "--frequency", type=int, default=25000, help="pwm frequency")
    parser.add_argument("-r", "--refresh", type=float, default=0.5, help="at which interval should the screen be refreshed")
    parser.add_argument("-i", "--increment", type=float, default=10, help="increment to use when increasing/decreasing fan speed")
    parser.add_argument("-f", "--font", type=Path, default=Path("fonts") / "scientifica.ttf", help="font to use for the display")
    parser.add_argument("--verbose", type=bool, default=False, action=argparse.BooleanOptionalAction, help="increase verbosity")
    parser.add_argument("-s", "--silent", type=bool, default=False, action=argparse.BooleanOptionalAction, help="silence warnings")
    parser.add_argument("-g", "--graphical", type=bool, default=False, action=argparse.BooleanOptionalAction, help="show a graphical indicator of fan speed")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args(argv)

    fan_controller(args.max, args.min, args.frequency, args.refresh, args.increment, args.font, args.verbose, args.silent, args.graphical)


if __name__ == "__main__":
    main(sys.argv[1:])
