#!/usr/bin/env python3

import RPi.GPIO as GPIO
from RPi.GPIO import PWM
from time import sleep
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.theme import Theme
from rich.console import Console
from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
from font_source_sans_pro import SourceSansProSemibold
import sys
import argparse


def init_console() -> Console:
    custom_theme = Theme({"bar.finished": "cyan", "bar.complete": "cyan", "progress.percentage": "yellow"})
    return Console(theme=custom_theme)


def init_pwm(frequency: int, max_duty: int) -> PWM:
    GPIO_PIN = 12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(GPIO_PIN, frequency)
    pwm.start(max_duty)
    return pwm


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


def fan_controller(max_duty: int, min_duty: int, frequency: int, pause: float, interval: float, verbose: bool):
    console = init_console()
    pwm = init_pwm(frequency, max_duty)
    display = DisplayContent()

    with Progress(TextColumn("{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("[bold]Fan Speed[/bold]", total=100)
        while True:
            for duty in range(max_duty, min_duty - 1, -1):
                if verbose:
                    print(f"duty: {duty}")
                pwm.ChangeDutyCycle(duty)
                progress.update(task, completed=duty)
                display.draw_text(f"Fan Speed: {duty}")
                sleep(interval)
            sleep(pause)
            for duty in range(min_duty, max_duty + 1):
                if verbose:
                    print(f"duty: {duty}")
                pwm.ChangeDutyCycle(duty)
                progress.update(task, completed=duty)
                display.draw_text(f"Fan Speed: {duty}")
                sleep(interval)
            sleep(pause)


def main(argv: list[str]):
    parser = argparse.ArgumentParser(prog="Fan Controller", description="Controls fans")
    parser.add_argument("-m", "--max", type=int, default=100, help="maximum duty cycle")
    parser.add_argument("-n", "--min", type=int, default=20, help="minimum duty cycle")
    parser.add_argument("-f", "--frequency", type=int, default=25000, help="pwm frequency")
    parser.add_argument("-p", "--pause", type=float, default=8, help="time to wait at minimum and maximum")
    parser.add_argument("-i", "--interval", type=float, default=0.2, help="time to wait between each percent increase or decrease")
    parser.add_argument("--verbose", type=bool, default=False, action=argparse.BooleanOptionalAction, help="increase verbosity")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args(argv)

    try:
        fan_controller(args.max, args.min, args.frequency, args.pause, args.interval, args.verbose)
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    main(sys.argv[1:])
