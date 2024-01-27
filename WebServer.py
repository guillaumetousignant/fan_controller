from typing import Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from functools import partial
import threading
import json
from PowerController import PowerController
from SpeedController import SpeedController


class FanHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, power: PowerController, speed: SpeedController, *args: Any, **kwargs: Any):
        self.power = power
        self.speed = speed
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == "/api/v1/on":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"on": self.power.enabled}).encode())
        elif self.path == "/api/v1/duty_cycle":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"duty_cycle": self.speed.duty_cycle}).encode())
        elif self.path == "/api/v1/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"on": self.power.enabled, "duty_cycle": self.speed.duty_cycle}).encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"404 - Not Found")

    def do_POST(self):
        if self.path == "/api/v1/on":
            self.power.turn_on()
            self.send_response(202)
            self.end_headers()
        elif self.path == "/api/v1/off":
            self.power.turn_off()
            self.send_response(202)
            self.end_headers()
        elif self.path == "/api/v1/toggle":
            self.power.toggle()
            self.send_response(202)
            self.end_headers()
        elif self.path == "/api/v1/duty_cycle":
            try:
                content_type = self.headers.get_content_type()
                if content_type != "application/json":
                    self.send_response(415)
                    self.end_headers()
                    return
                content_length = self.headers.get("content-length")
                if content_length is None:
                    self.send_response(500)
                    self.end_headers()
                    return
                length = int(content_length)
                message = json.loads(self.rfile.read(length))
                duty_cycle = float(message["duty_cycle"])
                self.speed.set_duty_cycle(duty_cycle)

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

    def __init__(self, address: tuple[str, int], power: PowerController, speed: SpeedController):
        self.running = True
        self.address = address

        handler = partial(FanHTTPRequestHandler, power, speed)
        self.httpd = HTTPServer(self.address, handler)

        self.web_server_thread = threading.Thread(target=self.web_server_main)
        self.web_server_thread.start()

    def stop(self):
        print("web server stopping")
        self.running = False
        self.httpd.shutdown()
        self.web_server_thread.join()

    def web_server_main(self):
        self.httpd.serve_forever()
