from inky import InkyWHAT
from PIL import Image, ImageFont, ImageDraw
import threading
from time import sleep
from FanController import FanController


class FanDisplay(object):
    display: InkyWHAT = None
    image: Image = None
    draw: ImageDraw = None
    FONT_SIZE: int = 128
    font: ImageFont = None
    polling_rate: float = 0
    display_thread: threading.Thread = None
    running: bool = False
    duty_cycle: float = 0
    enabled: bool = False
    fan: FanController = None

    def __init__(self, polling_rate: float, fan: FanController):
        self.display = InkyWHAT("black")
        self.image = Image.new("P", (self.display.width, self.display.height))
        self.draw = ImageDraw.Draw(self.image)
        self.font = ImageFont.truetype("fonts/scientifica.ttf", self.FONT_SIZE)
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
        while True:
            if self.fan.duty_cycle != self.duty_cycle or self.fan.enabled != self.enabled:
                self.duty_cycle = self.fan.duty_cycle
                self.enabled = self.fan.enabled
                self.draw_display()
            if not self.running:
                break
            sleep(self.polling_rate)

    def draw_display(self):
        text = f"{self.duty_cycle}%"
        X = 24
        Y = 0
        text_colour = self.display.WHITE if self.enabled else self.display.BLACK
        background_colour = self.display.BLACK if self.enabled else self.display.WHITE
        self.draw.rectangle((0, 0, self.display.width, self.display.height), fill=background_colour)
        self.draw.multiline_text((X, Y), text, fill=text_colour, font=self.font, align="left")
        self.display.set_image(self.image)
        self.display.show()
