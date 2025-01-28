from gpiozero import LED, MotionSensor, DistanceSensor, Servo
from time import sleep
from datetime import datetime, timedelta
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


# PIR Sensor
    pir = MotionSensor(6)  

# Distance Sensor (Ultrasonic)
    distance_sensor = DistanceSensor(echo = 4, trigger = 12)

# Servo Motor
    SERVO_PIN = 25  
    servo = Servo(SERVO_PIN, min_pulse_width = 0.5/1000, max_pulse_width = 2.5/1000)


###################################################### ^ GPIO Pins ^ ######################################################

# Function for a Single Traffic Light Sequence
    def traffic_light_sequence(direction):
        lights = traffic_lights[direction]
        print(f"Traffic light sequence for {direction} direction.")

# Turns Traffic Light from Red to Yellow to Green
    lights["red"].off()
    lights["yellow"].on()
    sleep(1)  # Yellow Light
    lights["yellow"].off()
    lights["green"].on()
    sleep(5)  # Green Light for Crossing

# Back to Red
    lights["green"].off()
    lights["yellow"].on()
    sleep(1)  # Yellow before red
    lights["yellow"].off()
    lights["red"].on()

#####################################################################

def motion():
    if (pir.motion_detected()):
        motion_detected = "True"
    else:
        motion_detected = "False"
        

###################################################### ^ Light Sequence + Set Angle Functions ^ ######################################################



# Function to Manage All Traffic Lights
    def crosswalk_traffic_control():
        for direction in traffic_lights:
            # Set All Other Directions to Red
                for other_dir, lights in traffic_lights.items():
                    if other_dir != direction:
                        lights["red"].on()
                        lights["yellow"].off()
                        lights["green"].off()


        # Run Sequence for The Current Direction
            traffic_light_sequence(direction)

###################################################### ^ Traffic Control Functions ^ ######################################################

# Main loop
    def Main_loop():
        try:
            start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)  # 6 Uhr
            end_time = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)  # 22 Uhr
            lights = traffic_lights.values()
        while now() < start_time:  # Wait Until 6:00 to Start ; Yellow Blinking
            lights["yellow"].off()
            sleep(1)
            lights["yellow"].on()
            sleep(1)

        while now() < end_time:  # Run Until 22:00
            crosswalk_traffic_control()
                
        while now() > end_time:  # Wait Until 6:00 to Start ; Yellow Blinking
            lights["yellow"].off()
            sleep(1)
            lights["yellow"].on()
            sleep(1)
    

        stop_event.set()    # Signal that Main_loop Ended 
            finally:
                pass

def data_log_loop():
    while not stop_event.is_set():  # Continue Only While Main_loop Is Running
        distance = distance_sensor.distance * 100 
        if pir.motion_detected:
            motion_detected="True"
        else:
            motion_detected="False"
        with open("traffic_data.csv", mode="a") as file:
            writer = csv.writer(file)
            writer.writerow(["Date + Time:",now,"Traffic detected:", motion_detected,"Train distance:", distance,"cm"])    
        sleep(1)    

# Create Threads for Both Loops
    thread1 = threading.Thread(target=Main_loop)
    thread2 = threading.Thread(target=data_log_loop)

# Start Both Threads
    thread1.start()
    thread2.start()

# Wait for the Main_loop to Finish
    thread1.join()
    thread2.join()