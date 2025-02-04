# Import required libraries for GPIO control, timing, and data handling
from gpiozero import LED, MotionSensor, DistanceSensor, Servo   # For hardware control <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[1](https://github.com/Gunjit27/Automated_Traffic_Light)</sup> <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[4](https://tutorials-raspberrypi.com/raspberry-pi-traffic-light-circuit-gpio-part-1/)</sup> 
from time import sleep
from datetime import datetime, timedelta
import csv
import threading

# Initialize global variables for timing and motion detection
now = datetime.now()
motion_detected = "False"
stop_event = threading.Event()

# Initialize four-way traffic light system with GPIO pin mappings
# N = North, E = East, S = South, W = West <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[1](https://github.com/Gunjit27/Automated_Traffic_Light)</sup> <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[7](https://www.c-sharpcorner.com/article/traffic-light-system-using-raspberry-pi/)</sup> 
traffic_lights = {
    "N": {"red": LED(24), "yellow": LED(23), "green": LED(18)},
    "E": {"red": LED(26), "yellow": LED(19), "green": LED(13)},
    "S": {"red": LED(17), "yellow": LED(27), "green": LED(22)},
    "W": {"red": LED(16), "yellow": LED(20), "green": LED(21)},
}

# Initialize sensors for traffic detection and management <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[5](https://www.ijnrd.org/papers/IJNRD2404301.pdf)</sup> 
# PIR Sensor for motion detection
pir = MotionSensor(6)  

# Ultrasonic sensor for distance measurement
distance_sensor = DistanceSensor(echo = 4, trigger = 12)

# Servo motor configuration for barrier control
SERVO_PIN = 25  
servo = Servo(SERVO_PIN, min_pulse_width = 0.5/1000, max_pulse_width = 2.5/1000)

###################################################### ^ GPIO Pins ^ ######################################################

# Controls individual traffic light sequence for given direction <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[2](https://github.com/PranavBhanot/Smart-traffic-light-management-with-Python-and-OpenCV)</sup> 
def traffic_light_sequence(direction):
    lights = traffic_lights[direction]
    print(f"Traffic light sequence for {direction} direction.")

    # Standard traffic light sequence: Red → Yellow → Green → Yellow → Red
    lights["red"].off()
    lights["yellow"].on()
    sleep(1)  # Yellow warning phase
    lights["yellow"].off()
    lights["green"].on()
    sleep(5)  # Green phase for vehicle crossing

    # Transition back to red
    lights["green"].off()
    lights["yellow"].on()
    sleep(1)  # Yellow warning before red
    lights["yellow"].off()
    lights["red"].on()

#####################################################################

# Motion detection function using PIR sensor <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[5](https://www.ijnrd.org/papers/IJNRD2404301.pdf)</sup> 
def motion():
    if (pir.motion_detected()):
        motion_detected = "True"
    else:
        motion_detected = "False"

###################################################### ^ Light Sequence + Set Angle Functions ^ ######################################################

# Main traffic control function for managing all directions <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[2](https://github.com/PranavBhanot/Smart-traffic-light-management-with-Python-and-OpenCV)</sup> 
def crosswalk_traffic_control():
    for direction in traffic_lights:
        # Ensure safety by setting red for all other directions
        for other_dir, lights in traffic_lights.items():
            if other_dir != direction:
                lights["red"].on()
                lights["yellow"].off()
                lights["green"].off()

        # Execute sequence for current direction
        traffic_light_sequence(direction)

###################################################### ^ Traffic Control Functions ^ ######################################################

# Main system control loop with time-based operation <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[5](https://www.ijnrd.org/papers/IJNRD2404301.pdf)</sup> 
def Main_loop():
    try:
        start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)  # Day starts at 6:00
        end_time = datetime.now().replace(hour=22, minute=0, second=0, microsecond=0)   # Day ends at 22:00
        lights = traffic_lights.values()
        
        while now() < start_time:  # Night mode: blinking yellow
            lights["yellow"].off()
            sleep(1)
            lights["yellow"].on()
            sleep(1)

        while now() < end_time:  # Day mode: normal operation
            crosswalk_traffic_control()
                
        while now() > end_time:  # Night mode: blinking yellow
            lights["yellow"].off()
            sleep(1)
            lights["yellow"].on()
            sleep(1)

        stop_event.set()    # Signal loop termination
    finally:
        pass

# Data logging function for system monitoring <sup className="rounded-full text-xs cursor-pointer [&>*]:!text-white h-4 w-4 px-1 bg-zinc-400 hover:bg-zinc-500 dark:bg-zinc-700 hover:dark:bg-zinc-600">[2](https://github.com/PranavBhanot/Smart-traffic-light-management-with-Python-and-OpenCV)</sup> 
def data_log_loop():
    while not stop_event.is_set():  # Run while main loop is active
        distance = distance_sensor.distance * 100 
        if pir.motion_detected:
            motion_detected="True"
        else:
            motion_detected="False"
        with open("traffic_data.csv", mode="a") as file:
            writer = csv.writer(file)
            writer.writerow(["Date + Time:",now,"Traffic detected:", motion_detected,"Train distance:", distance,"cm"])    
        sleep(1)    

# Initialize and start system threads
thread1 = threading.Thread(target=Main_loop)
thread2 = threading.Thread(target=data_log_loop)

# Launch threads
thread1.start()
thread2.start()

# Wait for completion
thread1.join()
thread2.join()
