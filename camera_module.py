import cv2
import os
from datetime import datetime
from config import Config

def capture_vehicle_image(entry=True):


    # Open camera - Try IP camera first, then fall back to default webcam
    # You can change the IP in .env file
    camera_source = Config.CAMERA_SOURCE
    
    camera = cv2.VideoCapture(camera_source)

    if not camera.isOpened():
        print(f"IP Camera {camera_source} not working, trying default webcam...")
        camera = cv2.VideoCapture(Config.FALLBACK_CAMERA)

    if not camera.isOpened():
        print("No camera found")
        return None

    # Capture frame
    ret, frame = camera.read()

    if not ret:
        print("Failed to capture image")
        camera.release()
        return None

    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if entry:
        folder = "static/images/entry/"
        filename = f"entry_{timestamp}.jpg"
    else:
        folder = "static/images/exit/"
        filename = f"exit_{timestamp}.jpg"

    filepath = os.path.join(folder, filename)

    # Save image
    cv2.imwrite(filepath, frame)

    # Release camera
    camera.release()

    return filepath
