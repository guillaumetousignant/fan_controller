#!/usr/bin/env python3

import sys
import argparse
from RotaryEncoder import RotaryEncoder
from FanDisplay import FanDisplay
from PowerButton import PowerButton
from SpeedController import SpeedController
from PWMChannel import PWMChannel
from RelayOutput import RelayOutput
from PowerController import PowerController
from ProgressBar import ProgressBar
from WebServer import WebServer
from MQTTCommunicator import MQTTCommunicator
import pigpio
from pathlib import Path
from typing import Optional
from pathlib import Path


def init_gpio(silent: bool) -> pigpio.pi:
    return pigpio.pi()


def fan_controller(
    max_duty: float,
    min_duty: float,
    frequency: int,
    refresh: float,
    increment: float,
    font_path: Optional[Path],
    client_id: str,
    broker: Optional[str],
    password_file: Path,
    verbose: bool,
    silent: bool,
    graphical: bool,
    http: bool,
):
    PWM_PIN = 12
    BUTTON_PIN = 4
    RELAY_PIN = 6
    CLK_PIN = 16
    DT_PIN = 26
    WEB_SERVER_ADDRESS = ("", 4208)
    INITIAL_POWER = False
    INITIAL_DUTY_CYCLE = 100

    pi = init_gpio(silent)

    progress_bar = None if not graphical else ProgressBar()
    if progress_bar is not None:
        progress_bar.display_fan_speed(INITIAL_DUTY_CYCLE)

    pwm = PWMChannel(PWM_PIN, frequency, min_duty, max_duty, INITIAL_DUTY_CYCLE, pi)
    speed = SpeedController(INITIAL_DUTY_CYCLE, pwm, progress_bar)
    encoder = RotaryEncoder(CLK_PIN, DT_PIN, increment, speed, pi)

    relay = RelayOutput(RELAY_PIN, INITIAL_POWER, pi)
    power = PowerController(INITIAL_POWER, relay)
    button = PowerButton(BUTTON_PIN, power, pi)

    display = FanDisplay(refresh, font_path, power, speed)
    web_server = None if not http else WebServer(WEB_SERVER_ADDRESS, power, speed)
    mqtt_communicator = None if not broker else MQTTCommunicator(client_id, broker, power, speed, password_file)

    if mqtt_communicator is not None:
        speed.set_communicate_callback(mqtt_communicator.communicate_speed)
        power.set_communicate_callback(mqtt_communicator.communicate_power)

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
        power.turn_off()
        if web_server is not None:
            web_server.stop()
        if mqtt_communicator is not None:
            mqtt_communicator.stop()
        display.stop()
        encoder.deactivate()
        pi.stop()  # type: ignore


def main(argv: list[str]):
    parser = argparse.ArgumentParser(prog="Fan Controller", description="Controls fans")
    parser.add_argument("-m", "--max", type=float, default=100, help="maximum duty cycle in %%")
    parser.add_argument("-n", "--min", type=float, default=20, help="minimum duty cycle in %%")
    parser.add_argument("-e", "--frequency", type=int, default=25000, help="pwm frequency")
    parser.add_argument("-r", "--refresh", type=float, default=0.5, help="at which interval should the screen be refreshed in seconds")
    parser.add_argument("-i", "--increment", type=float, default=10, help="increment to use when increasing/decreasing fan speed in %%")
    parser.add_argument("-f", "--font", type=Path, help="font to use for the display")
    parser.add_argument("-c", "--client-id", type=str, default="fan-controller", help="client id to use for MQTT")
    parser.add_argument("-b", "--broker", type=str, help="address and port of the MQTT message broker")
    parser.add_argument("-p", "--password-file", type=Path, default=Path(".password"), help="path to the file containing the MQTT broker password")
    parser.add_argument("--verbose", type=bool, default=False, action=argparse.BooleanOptionalAction, help="increase verbosity")
    parser.add_argument("-s", "--silent", type=bool, default=False, action=argparse.BooleanOptionalAction, help="silence warnings")
    parser.add_argument("-g", "--graphical", type=bool, default=False, action=argparse.BooleanOptionalAction, help="show a graphical indicator of fan speed")
    parser.add_argument(
        "-w", "--web", type=bool, default=False, action=argparse.BooleanOptionalAction, help="start an http server to control and access the fan"
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    args = parser.parse_args(argv)

    fan_controller(
        args.max,
        args.min,
        args.frequency,
        args.refresh,
        args.increment,
        args.font,
        args.client_id,
        args.broker,
        args.password_file,
        args.verbose,
        args.silent,
        args.graphical,
        args.web,
    )


if __name__ == "__main__":
    main(sys.argv[1:])
