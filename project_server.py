import serial
import time
import platform
import sys
import numpy as np
from modlib.apps import Annotator
from modlib.devices import AiCamera
from modlib.models import COLOR_FORMAT, MODEL_TYPE, Model
from modlib.models.post_processors import pp_od_yolo_ultralytics

# Determine the operating system
os_type = platform.system()

# Set the serial port based on the OS
if os_type == "Windows":
    port = "COM9"
elif os_type == "Darwin":  # macOS
    port = "/dev/tty.usbmodem11101"
elif os_type == "Linux":  # Raspberry Pi OS / Linux
    port = "/dev/ttyACM0"
else:
    raise Exception("Unsupported OS")

# Open a serial connection to the Pico W
try:
    s = serial.Serial(port, 115200)
    print(f"Successfully opened serial port: {s.name}")
    print("Connection confirmed! ??")

    time.sleep(2)  # Give Pico time to initialize after connection
    s.reset_input_buffer()  # Clear any old data in the buffer

except serial.SerialException as e:
    print(f"Error: Could not open serial port '{port}'.")
    print(f"Reason: {e}")
    print("\nPossible issues:")
    print("- The port name is incorrect.")
    print("- The device is not connected.")
    print("- The port is already in use by another program.")
    sys.exit(1)
    
target_label = input("What target is in screen: ")

class YOLO(Model):
    """YOLO model for IMX500 deployment."""

    def __init__(self):
        """Initialize the YOLO model for IMX500 deployment."""
        super().__init__(
            model_file="packerOut.zip",  # replace with proper directory
            model_type=MODEL_TYPE.CONVERTED,
            color_format=COLOR_FORMAT.RGB,
            preserve_aspect_ratio=False,
        )

        self.labels = np.genfromtxt(
            "labels.txt",  # replace with proper directory
            dtype=str,
            delimiter="\n",
        )

    def post_process(self, output_tensors):
        """Post-process the output tensors for object detection."""
        return pp_od_yolo_ultralytics(output_tensors)

device = AiCamera(frame_rate=8)
model = YOLO()
device.deploy(model)

annotator = Annotator()

with device as stream:
    for frame in stream:
        detections = frame.detections[frame.detections.confidence > 0.55]
        labels = [f"{model.labels[class_id]}: {score:0.2f}" for _, score, class_id, _ in detections]

        annotator.annotate_boxes(frame, detections, labels=labels, alpha=0.3, corner_radius=10)
        frame.display()
        
        # --- NEW CODE TO SEND DATA TO PICO ---
        if len(detections) > 0:
            for detection in detections:
                box, score, class_id, _ = detection
                class_label = model.labels[int(class_id)]
                
                # Check if the detected object is a 'tank'
                if class_label.lower() == 'tank':
                    # Extract the coordinates of the bounding box
                    x, y, w, h = box
                    
                    # Create a message to send over serial
                    message = f"{score}\n"
                    
                    # Encode the message as bytes and send it to the Pico
                    s.write(message.encode('utf-8'))
                    print(f"Sent to Pico: {message.strip()}")

        # ------------------------------------
        
        
#source venv/bin/activate
#python project_client.py
