import json
import paho.mqtt.client as mqtt
from gpiozero import Motor
from time import sleep

# Define enable pins for each motor
left_enable_pin = 22
right_enable_pin = 23

# Create motors with their respective enable pins
left_motor = Motor(forward=4, backward=14, enable=left_enable_pin)
right_motor = Motor(forward=17, backward=18, enable=right_enable_pin)


# MQTT settings
BROKER = "localhost"
PORT = 8080  # WebSocket port for Mosquitto
TOPIC = "mc/robot/navigate"


# Function to process incoming MQTT messages
def on_message(client, userdata, message):
    try:
        payload = message.payload.decode("utf-8")
        data = json.loads(payload)
        steering = data.get("s", 0)  # Default to 0 if not provided
        accelerator = data.get("a", 0)  # Default to 0 if not provided
        print(f"Received: a={accelerator}, s={steering}")
        
        # Ensure accelerator values are within -1 to 1 (for backward/forward)
        lVal = max(min(accelerator, 1), -1)
        rVal = max(min(accelerator, 1), -1)
        
        sHalf = steering / 2  # Split steering equally between motors
        
        # Adjust motor speeds based on steering
        lVal += sHalf
        rVal -= sHalf
        
        # Ensure motor values remain within the valid range
        lVal = max(min(lVal, 1), -1)
        rVal = max(min(rVal, 1), -1)
        
        print(f"Motor values: lVal={lVal}, rVal={rVal}")
        
        # Move the robot based on values for left and right motors
        move_robo(lVal, rVal)
        
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing message: {e}")


# Setup MQTT client
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(TOPIC)

client = mqtt.Client(transport="websockets")
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()


# Function to move the robot based on motor values
def move_robo(lVal, rVal):
    if lVal > 0:
        left_motor.forward(lVal)
    elif lVal < 0:
        left_motor.backward(-lVal)
    else:
        left_motor.stop()

    if rVal > 0:
        right_motor.forward(rVal)
    elif rVal < 0:
        right_motor.backward(-rVal)
    else:
        right_motor.stop()

try:
    # Keep the program running
    while True:
        sleep(1)

except KeyboardInterrupt:
    print("Program stopped")
    client.loop_stop()
    client.disconnect()
