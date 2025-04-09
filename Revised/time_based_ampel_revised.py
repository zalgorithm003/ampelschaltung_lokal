############################################### LIBRARY IMPORTS ###############################################
from gpiozero import LED, MotionSensor, DistanceSensor, Servo  # GPIO control components  
from time import sleep                                         # For timing control
from datetime import datetime, timedelta                       # For time-based operations
import csv                                                     # For data logging
import threading                                               # For parallel process management

############################################### GLOBAL VARIABLES ############################################
now = datetime.now()                # Current time reference
motion_detected = "False"           # Motion state flag
stop_event = threading.Event()      # Thread control event

############################################### GPIO SETUP #################################################
# Initialize Four-Way Traffic Light System with GPIO pin assignments 
traffic_lights = {
    "N": {"red": LED(24), "yellow": LED(23), "green": LED(18)},    # North direction lights
    "E": {"red": LED(26), "yellow": LED(19), "green": LED(13)},    # East direction lights
    "S": {"red": LED(17), "yellow": LED(27), "green": LED(22)},    # South direction lights
    "W": {"red": LED(16), "yellow": LED(20), "green": LED(21)},    # West direction lights
}

# Sensor Initialization 
pir = MotionSensor(6)                                              # PIR motion detector setup
distance_sensor = DistanceSensor(echo = 4, trigger = 12)           # Ultrasonic sensor setup

# Servo Motor Configuration for Barrier Control
SERVO_PIN = 25                                                     # Servo control pin
servo = Servo(SERVO_PIN, min_pulse_width = 0.5/1000, max_pulse_width = 2.5/1000)

############################################### TRAFFIC CONTROL FUNCTIONS ##################################
# Single Direction Traffic Light Control Sequence  
def traffic_light_sequence(direction):
    lights = traffic_lights[direction]
    print(f"Traffic light sequence for {direction} direction.")

    # Standard Traffic Light Sequence Implementation
    lights["red"].off()             # Turn off red
    lights["yellow"].on()           # Yellow warning phase
    sleep(1)                        # 1-second yellow duration
    lights["yellow"].off()          # Switch to green
    lights["green"].on()            
    sleep(5)                        # 5-second green duration

    # Return to Red Sequence
    lights["green"].off()           # End green phase
    lights["yellow"].on()           # Yellow warning
    sleep(1)                        # 1-second yellow duration
    lights["yellow"].off()          # Back to red
    lights["red"].on()
    sleep(3)                        # 3-second red duration

############################################### MOTION DETECTION ##########################################
def motion():
    if (pir.motion_detected()):     # Check PIR sensor status 
        motion_detected = "True"     # Set motion flag if detected
    else:
        motion_detected = "False"    # Clear motion flag if no detection

############################################### TRAFFIC MANAGEMENT #######################################
# Comprehensive Traffic Light Management 
def crosswalk_traffic_control():
    for direction in traffic_lights:
        # Safety: Set Red for All Other Directions
        for other_dir, lights in traffic_lights.items():
            if other_dir != direction:
                lights["red"].on()
                lights["yellow"].off()
                lights["green"].off()

        # Execute Sequence for Active Direction
        traffic_light_sequence(direction)

############################################### MAIN SYSTEM LOOPS #######################################
# Primary System Control Loop
def Main_loop():
    try:
        # Define Operating Hours
        start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)   # Day start: 6:00
        end_time = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)    # Day end: 22:00

        # Night Mode (Before 6:00) - Flashing Yellow
        while now < start_time:
            for lights in traffic_lights.values():
                lights["yellow"].off()
                sleep(1)
                lights["yellow"].on()
                sleep(1)

        # Day Mode Operation (6:00 - 22:00)
        while now < end_time:
            crosswalk_traffic_control()
                
        # Night Mode (After 22:00) - Flashing Yellow
        while now > end_time:
            for lights in traffic_lights.values():
                lights["yellow"].off()
                sleep(1)
                lights["yellow"].on()
                sleep(1)

        stop_event.set()            # Signal loop termination
    finally:
        pass

# Data Logging System Loop
def data_log_loop():
    while not stop_event.is_set():  # Run while main system is active
        distance = distance_sensor.distance * 100 
        if pir.motion_detected:
            motion_detected="True"
        else:
            motion_detected="False"
        with open("traffic_data.csv", mode="a") as file:
            writer = csv.writer(file)
            writer.writerow(["Date + Time:",now,"Traffic detected:", motion_detected,"Train distance:", distance,"cm"])    
        sleep(1)    

############################################### THREAD MANAGEMENT ######################################
# Initialize System Threads
thread1 = threading.Thread(target=Main_loop)       # Main control thread
thread2 = threading.Thread(target=data_log_loop)   # Data logging thread

# Launch System Threads
thread1.start()
thread2.start()

# Wait for System Completion
thread1.join()
thread2.join()
