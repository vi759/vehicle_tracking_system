import cv2
import numpy as np

def detect_vehicle_color(image_path):

    try:
        # Read image
        image = cv2.imread(image_path)

        if image is None:
            return "Unknown"

        # Resize image for faster processing
        image = cv2.resize(image, (200, 200))

        # Convert to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Get average color
        avg_color = image.mean(axis=0).mean(axis=0)

        r, g, b = avg_color

        # Simple color detection logic
        if r > 200 and g > 200 and b > 200:
            return "White"

        elif r < 80 and g < 80 and b < 80:
            return "Black"

        elif r > 150 and g < 100 and b < 100:
            return "Red"

        elif b > 150 and r < 100 and g < 100:
            return "Blue"

        elif r > 150 and g > 150 and b < 100:
            return "Yellow"

        elif r > 100 and g > 100 and b > 100:
            return "Gray"

        else:
            return "Unknown"

    except:
        return "Unknown"
