#!/usr/bin/env python3

from RPi import GPIO
from time import sleep
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.theme import Theme
from rich.console import Console
from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from font_source_sans_pro import SourceSansProSemibold
from enum import Enum, auto
import sys
import argparse


def init_console() -> Console:
    custom_theme = Theme({"bar.finished": "cyan", "bar.complete": "cyan", "progress.percentage": "yellow"})
    return Console(theme=custom_theme)


def init_gpio(silent: bool):
    GPIO.setwarnings(not silent)
    GPIO.setmode(GPIO.BCM)


def init_pwm(frequency: int, max_duty: int) -> GPIO.PWM:
    GPIO_PIN = 12
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(GPIO_PIN, frequency)
    pwm.start(max_duty)
    return pwm


class RotaryEncoder(object):
    class State(Enum):
        NoChange = auto()
        Up = auto()
        Down = auto()

    CLK_PIN: int = 16
    DT_PIN: int = 26
    clk_last_state: bool = False

    def __init__(self):
        GPIO.setup(self.CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.clk_last_state = GPIO.input(self.CLK_PIN)

    def poll(self, verbose: bool) -> State:
        clk_state = GPIO.input(self.CLK_PIN)
        dt_state = GPIO.input(self.DT_PIN)

        if clk_state == self.clk_last_state:
            return self.State.NoChange

        if verbose:
            print(f"Rotary encoder polled with state changed, last clk: {self.clk_last_state} clk: {clk_state} dt: {dt_state}")

        direction = dt_state == clk_state
        self.clk_last_state = clk_state

        if direction:  # Good candidate for match case
            return self.State.Down
        else:
            return self.State.Up


class DisplayContent(object):
    display: InkyWHAT = InkyWHAT("black")
    image: Image = Image.new("P", (display.width, display.height))
    draw: ImageDraw = ImageDraw.Draw(image)
    FONT_SIZE: int = 24
    font: ImageFont = ImageFont.truetype(SourceSansProSemibold, FONT_SIZE)

    def draw_text(self, text: str):
        x = 0
        y = 0
        self.draw.rectangle((0, 0, self.display.width, self.display.height), fill=(0, 0, 0, 0))
        self.draw.multiline_text((x, y), text, fill=self.display.BLACK, font=self.font, align="left")
        self.display.set_image(self.image)
        self.display.show()


def fan_controller(max_duty: int, min_duty: int, frequency: int, poll: float, increment: int, verbose: bool, silent: bool):
    console = init_console()
    init_gpio(silent)
    duty_cycle = max_duty
    pwm = init_pwm(frequency, duty_cycle)
    encoder = RotaryEncoder()
    display = DisplayContent()

    if verbose:
        print("System initialised")

    try:
        with Progress(TextColumn("{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as progress:
            task = progress.add_task("[bold]Fan Speed[/bold]", total=100)

            progress.update(task, completed=duty_cycle)
            display.draw_text(f"Fan Speed: {duty_cycle}%")

            while True:
                state = encoder.poll(verbose)
                if state == RotaryEncoder.State.Up:  # Good candidate for match case
                    duty_cycle += increment
                    if verbose:
                        print(f"duty: {duty_cycle}")
                    pwm.ChangeDutyCycle(duty_cycle)
                    progress.update(task, completed=duty_cycle)
                    display.draw_text(f"Fan Speed: {duty_cycle}%")
                elif state == RotaryEncoder.State.Down:
                    duty_cycle -= increment
                    if verbose:
                        print(f"duty: {duty_cycle}")
                    pwm.ChangeDutyCycle(duty_cycle)
                    progress.update(task, completed=duty_cycle)
                    display.draw_text(f"Fan Speed: {duty_cycle}%")
                sleep(poll)

    except KeyboardInterrupt:
        if verbose:
            print("Keyboard interrupt received")
    finally:
        if verbose:
            print("Cleaning up")
        pwm.ChangeDutyCycle(0)
        GPIO.cleanup()


def main(argv: list[str]):
    parser = argparse.ArgumentParser(prog="Fan Controller", description="Controls fans")
    parser.add_argument("-m", "--max", type=int, default=100, help="maximum duty cycle")
    parser.add_argument("-n", "--min", type=int, default=20, help="minimum duty cycle")
    parser.add_argument("-f", "--frequency", type=int, default=25000, help="pwm frequency")
    parser.add_argument("-p", "--poll", type=float, default=0.01, help="at which interval should the rotary encoder be polled")
    parser.add_argument("-i", "--increment", type=int, default=5, help="increment to use when increasing/decreasing fan speed")
    parser.add_argument("--verbose", type=bool, default=False, action=argparse.BooleanOptionalAction, help="increase verbosity")
    parser.add_argument("-s", "--silent", type=bool, default=False, action=argparse.BooleanOptionalAction, help="silence warnings")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args(argv)

    fan_controller(args.max, args.min, args.frequency, args.poll, args.increment, args.verbose, args.silent)


if __name__ == "__main__":
    main(sys.argv[1:])
