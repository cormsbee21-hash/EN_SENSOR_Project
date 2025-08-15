# EN_SENSOR_Project
Final Project for JHU EN_SENSORS_Project

README: Autonomous Drone Targeting System
This project details the development of a semi-autonomous drone system for target identification and engagement. It utilizes a dual-microcontroller architecture to separate complex computer vision tasks from real-time sensor control. The system leverages a Raspberry Pi 5 for high-level image processing with a YOLOv11 machine learning model and a Raspberry Pi Pico 2W for low-level sensor management and safety protocols.

System Architecture
The project is structured with a "server" and a "client" component that communicate via a serial connection:

High-Level Processing (project_server.py): This script runs on a Raspberry Pi 5 and a Raspberry Pi AI Camera. It acts as the drone's "eyes," processing video streams to identify targets using a pre-trained YOLOv11 model. Once a target is found, it sends a command over the serial port to the Pico.

Low-Level Control (project_compiled.py): This script runs on a Raspberry Pi Pico 2W. It acts as the "brainstem," handling critical, real-time tasks. It constantly monitors an ultrasonic ranger for distance and a crash sensor for physical impact, and uses this data to manage the drone's status, providing visual feedback via a traffic light LED array. It listens for commands from the server to initiate target engagement.

Codebase Breakdown
project_server.py
This Python script, intended for the Raspberry Pi 5, handles the vision-based targeting.

Serial Communication: It automatically detects the correct serial port (COM9, /dev/tty.usbmodem11101, or /dev/ttyACM0) to connect to the Pico.

Object Detection: The script uses the modlib library to deploy a YOLOv11 model on the AI Camera. It processes video frames in real-time and filters detections to a confidence score of 0.55 or higher.

Targeting Logic: It specifically looks for a tank object. When a tank is detected, it sends the detection's confidence score as a signal to the Pico via the serial connection.

project_compiled.py
This MicroPython script, designed for the Raspberry Pi Pico 2W, manages the drone's operational state. It is built using the uasyncio library to run multiple tasks concurrently.

Sensor Management:

Ultrasonic Ranger: The read_ultrasonic_ranger() function measures the distance to objects. If an object is less than 20 cm away, it sets the arm_status to 1, arming the system for potential engagement.

Crash Sensor: The read_crash() function monitors a physical crash sensor. If a crash is detected, it updates a crash_val variable to indicate a problem.

Visual Feedback: The set_light() function controls a traffic light LED array to communicate the drone's status:

Green Light: The system is unarmed (arm_status = 0).

Yellow Light: The system is armed, but a crash has been detected.

Red Light: The system is armed and ready for a target engagement command.

Serial Input: The read_serial() function listens for data from the server. Upon receiving a message, it sets the target_engagement flag, which would be used to trigger the final action of the drone.

How the System Works
The drone is powered on, and the Pico starts its control loop. The green LED is on, indicating the system is unarmed.

The Raspberry Pi 5 starts the server script, which connects to the Pico and begins processing video from the AI Camera.

As the drone flies, the ultrasonic sensor continuously checks for proximity to objects.

If the drone approaches a target (e.g., a "tank") within a predefined distance (less than 20 cm), the Pico's arm_status is set to 1, and the red LED turns on.

Simultaneously, the Raspberry Pi 5's camera detects the "tank" and sends a signal to the Pico.

The Pico receives the signal, and if the system is armed, the target_engagement flag is set, theoretically activating the final "engagement" phase of the mission.

The crash sensor acts as an override, flashing a yellow light if a physical impact is detected, regardless of the arming status.
