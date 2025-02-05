from time import sleep
from gpiozero import LED, MotionSensor, DistanceSensor
distance_sensor = DistanceSensor(echo = 4, trigger = 12)

while True:
    distance = distance_sensor.distance * 100  # Convert to cm
    print(f"Distance: {distance:.2f} cm")
    sleep(1)  # Delay for 1 second
