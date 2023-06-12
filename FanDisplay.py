from inky import InkyWHAT  # type: ignore
from PIL import Image, ImageFont, ImageDraw
import threading
from time import sleep
from pathlib import Path
from typing import Optional
from FanController import FanController
from font_source_sans_pro import SourceSansProSemibold  # type: ignore


class FanDisplay(object):
    FONT_SIZE: int = 128
    polling_rate: float = 0
    running: bool = False
    duty_cycle: float = 0
    enabled: bool = False

    def __init__(self, polling_rate: float, font_path: Optional[Path], fan: FanController):
        self.display = InkyWHAT("black")  # type: ignore
        size = int(self.display.height), int(self.display.width)  # type: ignore
        self.image = Image.new("P", size)
        self.draw = ImageDraw.Draw(self.image)
        if font_path is not None:
            self.font = ImageFont.truetype(str(font_path), self.FONT_SIZE)
        else:
            self.font = ImageFont.truetype(SourceSansProSemibold, self.FONT_SIZE)  # type: ignore
        self.polling_rate = polling_rate
        self.running = True
        self.fan = fan
        self.duty_cycle = fan.duty_cycle
        self.enabled = fan.enabled

        self.draw_display()

        self.display_thread = threading.Thread(target=self.display_main)
        self.display_thread.start()

    def stop(self):
        print("stopping")
        self.running = False
        self.display_thread.join()

    def display_main(self):
        while self.running:
            if self.fan.duty_cycle != self.duty_cycle or self.fan.enabled != self.enabled:
                self.duty_cycle = self.fan.duty_cycle
                self.enabled = self.fan.enabled
                self.draw_display()
            sleep(self.polling_rate)

    def draw_display(self):
        text = f"{int(self.duty_cycle)}%"
        X = 24
        Y = 0
        text_colour = self.display.WHITE if self.enabled else self.display.BLACK  # type: ignore
        background_colour = self.display.BLACK if self.enabled else self.display.WHITE  # type: ignore
        self.draw.rectangle((0, 0) + self.image.size, fill=background_colour)  # type: ignore
        self.draw.multiline_text((X, Y), text, fill=text_colour, font=self.font, align="left")  # type: ignore
        self.display.set_image(self.image.transpose(2))  # type: ignore
        self.display.show()  # type: ignore
