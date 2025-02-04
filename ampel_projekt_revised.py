###################################################### ^ Traffic Control Functions ^ ######################################################

# Function to manage the entire traffic light system during normal operation
def crosswalk_traffic_control():
    for direction in traffic_lights:
        # Safety measure: Set all non-active directions to red before changing any signal
        for other_dir, lights in traffic_lights.items():
            if other_dir != direction:
                lights["red"].on()
                lights["yellow"].off()
                lights["green"].off()

        # Execute the traffic light sequence for the current direction
        traffic_light_sequence(direction)

#####################################################################

# Specialized function for handling traffic light sequence during train crossing
def train_crosswalk_traffic_control():
    # Safety protocol: All directions must show red when a train is approaching
    for lights in traffic_lights.values():
        lights["red"].on()
        lights["yellow"].off()
        lights["green"].off()      

    # Control barrier movement for train crossing
    set_angle(180)  # Raise the barrier
    print("Wait for the Train to pass.")
    sleep(5)   # Safety delay during train passage
    set_angle(0)  # Lower the barrier after train passes

###################################################### ^ Main Control Logic ^ ######################################################

# Main control loop for the traffic system
def Main_loop():
    try:
        # Initialize system with all lights set to red
        for lights in traffic_lights.values():
            lights["red"].on()
            lights["yellow"].off()
            lights["green"].off()

        for i in range(3):  # Execute control cycle three times
            # Safety check: Ensure all signals start from red
            for lights in traffic_lights.values():
                lights["red"].on()
                lights["yellow"].off()
                lights["green"].off()

            # Monitor train proximity using distance sensor
            distance = distance_sensor.distance * 100  # Convert meters to centimeters
            print(f"Distance: {distance:.2f} cm")
            
            if distance < 50:  # Train detection threshold (50 cm)
                print("Train detected! Starting train crosswalk sequence.")
                train_crosswalk_traffic_control()
                
                # Check for pedestrian/vehicle traffic after train passes
                if pir.motion_detected:
                    print("Motion detected! Starting crosswalk sequence.")
                    crosswalk_traffic_control()
                else:
                    print("No significant traffic detected.")
                    
                sleep(1)  # System update interval

            i += 1
        stop_event.set()   # Signal completion of main control loop
    finally:
        pass

# Continuous data logging function running in parallel
def data_log_loop():
    while not stop_event.is_set():    # Run until main loop signals completion
        # Gather current sensor readings
        distance = distance_sensor.distance * 100 
        if pir.motion_detected:
            motion_detected = "True"
        else:
            motion_detected = "False"
            
        # Log data to CSV file with timestamp and sensor readings
        with open("traffic_data.csv", mode="a") as file:
            writer = csv.writer(file)
            writer.writerow(["Date + Time:", now,
                           "Traffic detected:", motion_detected,
                           "Train distance:", distance, "cm"])    
        sleep(1)    # Data logging interval

# Thread initialization and management
def initialize_threads():
    # Create separate threads for main control and data logging
    thread1 = threading.Thread(target=Main_loop)
    thread2 = threading.Thread(target=data_log_loop)

    # Start both threads
    thread1.start()
    thread2.start()

    # Wait for both threads to complete execution
    thread1.join()
    thread2.join()

# System execution entry point
if __name__ == "__main__":
    initialize_threads()
