from gpiozero import LED, MotionSensor, DistanceSensor, Servo
from time import sleep
from datetime import datetime
import csv
import threading

now = datetime.now()
motion_detected = "False"
stop_event = threading.Event()

# Initialize Tetradirectional Traffic Light System
    traffic_lights = {
        "N": {"red": LED(24), "yellow": LED(23), "green": LED(18)},
        "E": {"red": LED(26), "yellow": LED(19), "green": LED(13)},
        "S": {"red": LED(17), "yellow": LED(27), "green": LED(22)},
        "W": {"red": LED(16), "yellow": LED(20), "green": LED(21)},
        }

# Initialize PIR Sensor
    pir = MotionSensor(6)  

# Initialize Distance Sensor (Ultrasonic)
    distance_sensor = DistanceSensor(echo = 4, trigger = 12)

# Initialize Servo Motor
    SERVO_PIN = 25  
    servo = Servo(SERVO_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

###################################################### ^ GPIO Pins ^ ######################################################

# Function for a Single Traffic Light Sequence
    def traffic_light_sequence(direction):
        lights = traffic_lights[direction]
        print(f"Traffic light sequence for {direction} direction.")

# Turns Traffic Light from Red to Yellow to Green
    lights["red"].off()
    lights["yellow"].on()
    sleep(1)  # Yellow light
    lights["yellow"].off()
    lights["green"].on()
    sleep(5)  # Green light for crossing

# Back to Red
    lights["green"].off()
    lights["yellow"].on()
    sleep(1)  # Yellow before red
    lights["yellow"].off()
    lights["red"].on()


#####################################################################

def set_angle(angle):
    """Set the servo motor to the specified angle (0-180)."""
    # Map angle (0-180) to servo position (-1 to 1)
    position = (angle / 180.0) * 2 - 1
    servo.value = position
    sleep(0.5)  # Allow the servo to reach the position 

#####################################################################

def motion():
    if (pir.motion_detected()):
        motion_detected = "True"
    else:
        motion_detected = "False"
        

###################################################### ^ Light Sequence + Set Angle Functions ^ ######################################################


# Function to Manage all Traffic Light
def crosswalk_traffic_control():
    for direction in traffic_lights:
        # Set all other directions to red
        for other_dir, lights in traffic_lights.items():
            if other_dir != direction:
                lights["red"].on()
                lights["yellow"].off()
                lights["green"].off()


        # Run sequence for the current direction
        traffic_light_sequence(direction)

#####################################################################

# Function For The Traffic Light Sequence if There Is a Train
    def train_crosswalk_traffic_control():
        # Set All Directions to Red 
            for lights in traffic_lights.values():
                lights["red"].on()
                lights["yellow"].off()
                lights["green"].off()      

set_angle(180)
print("Wait for the Train to pass.")
sleep(5)   
set_angle(0)

###################################################### ^ Traffic Control Functions ^ ######################################################


# Main loop
def Main_loop():
    try:
        for lights in traffic_lights.values():
            lights["red"].on()
            lights["yellow"].off()
            lights["green"].off()

        for i in range(3) :
            # Ensure All Lights Are Initially Red
                for lights in traffic_lights.values():
                    lights["red"].on()
                    lights["yellow"].off()
                    lights["green"].off()

            distance = distance_sensor.distance * 100  # Convert to cm
            print(f"Distance: {distance:.2f} cm")
            if distance < 50:  # Train Detected
                
                print("Train detected! Starting train crosswalk sequence.")
                train_crosswalk_traffic_control()
            

            if pir.motion_detected:

                print("Motion detected! Starting crosswalk sequence.")
                crosswalk_traffic_control()
                
            else:
                print("No significant traffic detected.")
            sleep(1)  # Delay for the Next Iteration

            i=i+1
        stop_event.set()   # Signal that Main_loop Ended
    finally:
        pass

def data_log_loop():
    while not stop_event.is_set():    # Continue Only While Main_loop Is Running
        distance = distance_sensor.distance * 100 
        if pir.motion_detected:
            motion_detected="True"
        else:
            motion_detected="False"
        with open("traffic_data.csv", mode="a") as file:
            writer = csv.writer(file)
            writer.writerow(["Date + Time:",now,"Traffic detected:", motion_detected,"Train distance:", distance,"cm"])    
        sleep(1)    

#Create Threads for Both Loops
    thread1 = threading.Thread(target=Main_loop)
    thread2 = threading.Thread(target=data_log_loop)

# Start Both Threads
    thread1.start()
    thread2.start()

# Wait for The Main_loop to Finish
    thread1.join()
    thread2.join()