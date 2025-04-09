from gpiozero import LED, MotionSensor, DistanceSensor, Servo
from time import sleep
from datetime import datetime
import csv
import threading

motion_detected = "False"
stop_event = threading.Event()

# Initialize Tetradirectional Traffic Light System (N, E, S, W directions)
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

###################################################### ^ GPIO Pins ^ ######################################################

# Function to control the traffic light sequence for a specific direction (N, E, S, W)
def traffic_light_sequence(direction):
    lights = traffic_lights[direction]
    print(f"Traffic light sequence for {direction} direction.")

    # Transition from Red to Yellow to Green
    lights["red"].off()   # Turn off Red light
    lights["yellow"].on() # Turn on Yellow light
    sleep(1)  # Yellow light duration
    lights["yellow"].off()  # Turn off Yellow light
    lights["green"].on()  # Turn on Green light
    sleep(5)  # Green light for crossing

    # Transition from Green to Yellow to Red
    lights["green"].off()  # Turn off Green light
    lights["yellow"].on() # Turn on Yellow light
    sleep(1)  # Yellow light duration before turning Red
    lights["yellow"].off()  # Turn off Yellow light
    lights["red"].on()   # Turn on Red light

#####################################################################

# Function to set the servo motor's angle (0-180 degrees)
def set_angle(angle):
    """Set the servo motor to the specified angle (0-180)."""
    # Map angle (0-180) to servo position (-1 to 1)
    position = (angle / 180.0) * 2 - 1
    servo.value = position
    sleep(0.5)  # Allow the servo to reach the desired position

#####################################################################

# Function to detect motion using the PIR sensor
def motion():
    if pir.motion_detected():
        motion_detected = "True"  # Motion detected
    else:
        motion_detected = "False"  # No motion detected

###################################################### ^ Light Sequence + Set Angle Functions ^ ######################################################


# Function to manage traffic lights for pedestrian crosswalk in all directions
def crosswalk_traffic_control():
    for direction in traffic_lights:
        # Set all other directions to red while running current direction's sequence
        for other_dir, lights in traffic_lights.items():
            if other_dir != direction:
                lights["red"].on()  # Turn on red lights for other directions
                lights["yellow"].off()  # Turn off yellow and green lights
                lights["green"].off()

        # Run the light sequence for the current direction
        traffic_light_sequence(direction)

#####################################################################

# Function to manage traffic light sequence when a train is detected
def train_crosswalk_traffic_control():
    # Set all directions to red when train is detected
    for lights in traffic_lights.values():
        lights["red"].on()  # Red light for all directions
        lights["yellow"].off()  # Turn off yellow and green lights
        lights["green"].off()  

    # Move the servo to close the barrier for the train
    set_angle(180)  
    print("Wait for the train to pass.")
    sleep(5)  # Wait for the train to pass
    set_angle(0)  # Open the barrier after the train passes

###################################################### ^ Traffic Control Functions ^ ######################################################


# Main loop to control traffic and detect obstacles (motion/trains)
def Main_loop():
    try:
        # Set all traffic lights to red initially
        for lights in traffic_lights.values():
            lights["red"].on()
            lights["yellow"].off()
            lights["green"].off()

        for i in range(5):
            # Ensure all lights are initially red
            for lights in traffic_lights.values():
                lights["red"].on()
                lights["yellow"].off()
                lights["green"].off()

            # Measure the distance using ultrasonic sensor to detect trains
            distance = distance_sensor.distance * 100  # Convert distance to cm
            print(f"Distance: {distance:.2f} cm")
            if distance < 50:  # If train is detected within 50cm
                print("Train detected! Starting train crosswalk sequence.")
                train_crosswalk_traffic_control()

            # If motion is detected, manage pedestrian crosswalk traffic
            if pir.motion_detected:
                print("Motion detected! Starting crosswalk sequence.")
                crosswalk_traffic_control()
            else:
                print("No significant traffic detected.")
            sleep(1)  # Delay for the next iteration
            i = i + 1
        stop_event.set()   # Signal that the Main_loop has ended
    finally:
        pass

# Function to log traffic data (motion and train distance) into a CSV file
def data_log_loop():
    while not stop_event.is_set():    # Continue logging data while Main_loop is running
        distance = distance_sensor.distance * 100  # Convert distance to cm
        if pir.motion_detected:
            motion_detected = "True"  # Log motion detection
        else:
            motion_detected = "False"  # No motion detected
        with open("traffic_data.csv", mode="a") as file:
            writer = csv.writer(file)
            # Log date, time, motion status, and train distance
            writer.writerow(["Date + Time:", datetime.now(), "Traffic detected:", motion_detected, "Train distance:", distance, "cm"])    
        sleep(1)  # Log data every second

# Create threads for both loops (Main loop and Data logging loop)
thread1 = threading.Thread(target=Main_loop)
thread2 = threading.Thread(target=data_log_loop)

# Start both threads concurrently
thread1.start()
thread2.start()

# Wait for both threads to finish
thread1.join()
thread2.join()
