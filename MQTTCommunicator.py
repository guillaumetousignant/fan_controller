import paho.mqtt.client as mqtt
from PowerController import PowerController
from SpeedController import SpeedController
from pathlib import Path


class MQTTCommunicator(object):
    client_id: str = ""
    message_broker: str = ""

    def __init__(self, client_id: str, message_broker: str, power: PowerController, speed: SpeedController, password_file: Path):
        self.client_id = client_id
        self.message_broker = message_broker
        self.power = power
        self.speed = speed
        self.client = mqtt.Client(client_id=self.client_id)

        password = ""
        with open(password_file, "r") as f:
            password = f.read().strip()
        self.client.username_pw_set(client_id, password)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        self.client.connect(self.message_broker)
        self.client.loop_start()

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        client.subscribe(f"{self.client_id}/on/set", qos=0)
        client.subscribe(f"{self.client_id}/speed/percentage", qos=0)

        client.message_callback_add(f"{self.client_id}/on/set", self.set_power)
        client.message_callback_add(f"{self.client_id}/speed/percentage", self.set_speed)

        client.publish(f"{self.client_id}/availability/state", "online", qos=1, retain=True)

    def set_power(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        if message.payload == b"ON":
            self.power.turn_on()
        elif message.payload == b"OFF":
            self.power.turn_off()
        else:
            print(f'Received unknown set_power with topic "{message.topic}" and message "{message.payload}"')

    def set_speed(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        duty_cycle = 0
        try:
            duty_cycle = float(message.payload)
        except ValueError:
            print(f'Received unknown set_speed with topic "{message.topic}" and message "{message.payload}"')
            return
        self.speed.set_duty_cycle(float(message.payload))

    def on_disconnect(self, client: mqtt.Client, userdata, rc):
        client.publish(f"{self.client_id}/availability/state", "offline", qos=1, retain=True)

    def on_message(self, client: mqtt.Client, userdata, message: mqtt.MQTTMessage):
        print(f'Received unknown message with topic "{message.topic}" and message "{message.payload}"')

    def stop(self):
        self.client.loop_stop()

    def communicate_power(self, power: bool):
        self.client.publish(f"{self.client_id}/on/state", "ON" if power else "OFF", qos=0, retain=True)

    def communicate_speed(self, duty_cycle: float):
        self.client.publish(f"{self.client_id}/speed/percentage_state", str(int(duty_cycle)), qos=0, retain=True)
