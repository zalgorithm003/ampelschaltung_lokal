from time import sleep
from gpiozero import LED

traffic_lights = {
    "N": {"red": LED(24), "yellow": LED(23), "green": LED(18)},
    "E": {"red": LED(26), "yellow": LED(19), "green": LED(13)},
    "S": {"red": LED(17), "yellow": LED(27), "green": LED(22)},
    "W": {"red": LED(16), "yellow": LED(20), "green": LED(21)},
}

# Initialize PIR Sensor for motion detection
pir = MotionSensor(6)  

# Initialize Distance Sensor (Ultrasonic) for train detection
distance_sensor = DistanceSensor(echo = 4, trigger = 12)

# Initialize Servo Motor for controlling physical barrier
SERVO_PIN = 25  
servo = Servo(SERVO_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

while True:
   # traffic_lights["N"]["red"].on()      
    traffic_lights["E"]["yellow"].on()  

