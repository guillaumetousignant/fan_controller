from typing import Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from functools import partial
import threading
import json
from FanController import FanController
from PowerButton import PowerButton
from PWMChannel import PWMChannel
from ProgressBar import ProgressBar


class FanHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, fan: FanController, button: PowerButton, pwm: PWMChannel, progress_bar: Optional[ProgressBar], *args, **kwargs):
        self.fan = fan
        self.button = button
        self.pwm = pwm
        self.progress_bar = progress_bar
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/api/v1/on":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"on": self.fan.enabled}).encode())
        elif self.path == "/api/v1/duty_cycle":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"duty_cycle": self.fan.duty_cycle}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"404 - Not Found")
    def do_POST(self):
        if self.path == "/api/v1/on":
            if not self.fan.enabled:
                self.button.switch()
            self.send_response(202)
            self.end_headers()
        elif self.path == "/api/v1/off":
            if self.fan.enabled:
                self.button.switch()
            self.send_response(202)
            self.end_headers()
        elif self.path == "/api/v1/toggle":
            self.button.switch()
            self.send_response(202)
            self.end_headers()
        elif self.path == "/api/v1/duty_cycle":
            try:
                content_type = self.headers.get_content_type()
                if content_type != "application/json":
                    self.send_response(415)
                    self.end_headers()
                    return
                length = int(self.headers.get("content-length"))
                message = json.loads(self.rfile.read(length))
                duty_cycle = float(message["duty_cycle"])
                changed = self.fan.set_duty_cycle(duty_cycle)
                if changed:
                    self.pwm.set_duty_cycle(self.fan.duty_cycle)
                    if self.progress_bar is not None:
                        self.progress_bar.display_fan_speed(self.fan.duty_cycle)

                self.send_response(202)
                self.end_headers()
            except:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"404 - Not Found")

class WebServer(object):
    running: bool = False
    address: tuple[str, int] = ("", 4208)
    progres_bar: Optional[ProgressBar] = None

    def __init__(self, address: tuple[str, int], fan: FanController, button: PowerButton, pwm: PWMChannel, progress_bar: Optional[ProgressBar]):
        self.running = True
        self.address = address
        self.fan = fan
        self.button = button
        self.pwm = pwm
        self.progress_bar = progress_bar
        self.web_server_thread = threading.Thread(target=self.web_server_main)
        self.web_server_thread.start()

    def stop(self):
        print("web server stopping")
        self.running = False
        self.web_server_thread.join()

    def web_server_main(self):
        handler = partial(FanHTTPRequestHandler, self.fan, self.button, self.pwm, self.progress_bar)
        httpd = HTTPServer(self.address, handler)
        while self.running:
            httpd.handle_request()
