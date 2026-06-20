import easyocr


# Global variable for lazy loading
reader = None

def detect_number_plate(image_path):
    global reader
    
    try:
        if reader is None:
            # Create OCR reader (English) only when needed
            # gpu=False to be safer on diverse hardware, or detected automatically
            reader = easyocr.Reader(['en'], gpu=False)

        # Read text from image
        results = reader.readtext(image_path)

        detected_text = ""

        for (bbox, text, confidence) in results:

            # Filter only strong detections
            if confidence > 0.4:
                detected_text += text + " "

        detected_text = detected_text.strip()

        return detected_text

    except Exception as e:
        print(f"OCR Error: {e}")
        return None
