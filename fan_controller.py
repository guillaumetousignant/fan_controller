#!/usr/bin/env python3

import RPi.GPIO as GPIO
from time import sleep
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.theme import Theme
from rich.console import Console
import sys
import argparse

def fan_controller(max_duty: int, min_duty: int, frequency: int, verbose: bool):
    custom_theme = Theme({"bar.finished": "cyan", "bar.complete": "cyan", "progress.percentage": "yellow"})
    console = Console(theme=custom_theme)
    
    GPIO_PIN = 12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(GPIO_PIN, frequency)
    pwm.start(max_duty)

    with Progress(TextColumn("{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as progress:
        task = progress.add_task("[bold]Fan Speed[/bold]", total=100)
        while True:
            for duty in range(max_duty, min_duty - 1, -1):
                if verbose:
                    print(f"duty: {duty}")
                pwm.ChangeDutyCycle(duty)
                progress.update(task, completed=duty)
                sleep(0.1)
            sleep(5)
            for duty in range(min_duty, max_duty + 1):
                if verbose:
                    print(f"duty: {duty}")
                pwm.ChangeDutyCycle(duty)
                progress.update(task, completed=duty)
                sleep(0.1)
            sleep(5)

def main(argv: list[str]):
    parser = argparse.ArgumentParser(prog="Fan Controller", description="Controls fans")
    parser.add_argument("-m", "--max", type=int, default=100, help="maximum duty cycle")
    parser.add_argument("-n", "--min", type=int, default=20, help="minimum duty cycle")
    parser.add_argument("-f", "--frequency", type=int, default=25000, help="pwm frequency")
    parser.add_argument("--verbose", type=bool, default=False, action=argparse.BooleanOptionalAction, help="increase verbosity")
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args(argv)

    try:
        fan_controller(args.max, args.min, args.frequency, args.verbose)
    except KeyboardInterrupt:
        return

if __name__ == "__main__":
    main(sys.argv[1:])
