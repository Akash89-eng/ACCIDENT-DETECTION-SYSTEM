import cv2
import numpy as np
import re
from config import *


class ANPRSystem:
    """
    Automatic Number Plate Recognition (ANPR)
    Features:
    - Number plate detection
    - OCR text extraction
    - Vehicle number matching with database
    - Driver identification
    """

    def __init__(self):
        self.enabled = ANPR_ENABLED
        self.confidence_threshold = ANPR_CONFIDENCE_THRESHOLD

        # Initialize OCR (pytesseract)
        self.use_ocr = False
        try:
            import pytesseract
            self.ocr = pytesseract
            self.use_ocr = True
            print("✅ OCR initialized for number plate recognition")
        except:
            print("⚠️ Tesseract not installed. Install with: pip install pytesseract")
            print("   Also install Tesseract-OCR from: https://github.com/UB-Mannheim/tesseract/wiki")

        print("✅ ANPR System initialized")

    def detect_license_plate(self, frame, vehicle_bbox):
        """
        Detect license plate from vehicle bounding box
        Returns: plate_text, confidence, plate_bbox
        """
        if not self.enabled or not self.use_ocr:
            return None, 0, None

        try:
            # Extract vehicle region
            x1, y1, x2, y2 = vehicle_bbox
            vehicle_roi = frame[y1:y2, x1:x2]

            if vehicle_roi.size == 0:
                return None, 0, None

            # Find license plate region (bottom part of vehicle)
            plate_height = int((y2 - y1) * 0.15)
            plate_y1 = y2 - plate_height
            plate_y2 = y2

            if plate_y1 < y1:
                plate_y1 = y1

            plate_roi = frame[plate_y1:plate_y2, x1:x2]

            if plate_roi.size == 0:
                return None, 0, None

            # Preprocess for OCR
            processed = self._preprocess_plate(plate_roi)

            # Extract text using OCR
            plate_text = self._extract_text(processed)

            if plate_text and len(plate_text) >= 4:
                confidence = self._calculate_confidence(plate_text, processed)
                plate_bbox = (x1, plate_y1, x2, plate_y2)
                return plate_text, confidence, plate_bbox

            return None, 0, None

        except Exception as e:
            print(f"ANPR error: {e}")
            return None, 0, None

    def _preprocess_plate(self, plate_image):
        """Preprocess image for better OCR"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)

            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)

            # Apply adaptive threshold
            thresh = cv2.adaptiveThreshold(blurred, 255,
                                           cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 11, 2)

            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

            # Resize for better OCR
            height, width = cleaned.shape
            if width > 0 and height > 0:
                scale_factor = max(300 / width, 100 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                resized = cv2.resize(cleaned, (new_width, new_height))
                return resized

            return cleaned

        except:
            return plate_image

    def _extract_text(self, processed_image):
        """Extract text from processed image using OCR"""
        try:
            # Configure OCR for license plates
            config = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

            # Extract text
            text = self.ocr.image_to_string(processed_image, config=config)

            # Clean text
            text = re.sub(r'[^A-Z0-9]', '', text.upper())

            # Common Indian license plate patterns
            patterns = [
                r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$',  # TN01AB1234
                r'^[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}$',  # TN01AB1234
                r'^[A-Z]{2}[0-9]{2}[A-Z]{1}[0-9]{4}$',  # TN01A1234
                r'^[A-Z]{2}[0-9]{2}[0-9]{4}$'  # TN011234
            ]

            for pattern in patterns:
                if re.match(pattern, text):
                    return text

            # Return cleaned text if it looks like a plate
            if len(text) >= 6 and len(text) <= 12:
                return text

            return None

        except:
            return None

    def _calculate_confidence(self, plate_text, processed_image):
        """Calculate confidence score for plate recognition"""
        # Simple confidence based on text length and pattern match
        confidence = 0.5

        if len(plate_text) >= 8:
            confidence += 0.2
        if len(plate_text) <= 10:
            confidence += 0.1

        # Check pattern
        if re.match(r'^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$', plate_text):
            confidence += 0.2

        return min(confidence, 0.95)

    def match_with_database(self, license_plate, database):
        """
        Match license plate with database
        Returns: vehicle_info, owner_info
        """
        if not license_plate:
            return None, None

        vehicle = database.get_vehicle(license_plate)

        if vehicle:
            return vehicle, {
                'owner_name': vehicle.get('owner_name'),
                'phone': vehicle.get('phone'),
                'email': vehicle.get('email'),
                'vehicle_model': vehicle.get('vehicle_model'),
                'vehicle_color': vehicle.get('vehicle_color')
            }

        return None, None

    def draw_plate_info(self, frame, license_plate, confidence, bbox, vehicle_info=None):
        """Draw license plate information on frame"""
        x1, y1, x2, y2 = bbox

        # Draw rectangle around plate
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Display plate text
        text = f"Plate: {license_plate} ({confidence:.0f}%)"
        cv2.putText(frame, text, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Display owner info if available
        if vehicle_info:
            y_offset = y2 + 20
            owner_name = vehicle_info.get('owner_name', '')
            if owner_name:
                cv2.putText(frame, f"Owner: {owner_name}", (x1, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_offset += 20

            phone = vehicle_info.get('phone', '')
            if phone:
                cv2.putText(frame, f"Phone: {phone}", (x1, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return frame