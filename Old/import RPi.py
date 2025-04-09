from time import sleep
from gpiozero import LED, MotionSensor, DistanceSensor

pir = MotionSensor(6)  

# Initialize Distance Sensor (Ultrasonic) for train detection
distance_sensor = DistanceSensor(echo = 4, trigger = 12)

# Initialize Servo Motor for controlling physical barrier
SERVO_PIN = 25  


while True:
    if pir.motion_detected:
        print("Motion detected! Starting crosswalk sequence.")
    else:
        print("No significant traffic detected.")
    sleep(0.2)