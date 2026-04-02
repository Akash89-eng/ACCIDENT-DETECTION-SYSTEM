import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.absolute()
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
TEST_VIDEOS_FOLDER = os.path.join(BASE_DIR, 'test_videos')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')
EVIDENCE_FOLDER = os.path.join(BASE_DIR, 'evidence')
DATABASE_FOLDER = os.path.join(BASE_DIR, 'database')

# Create folders
for folder in [UPLOAD_FOLDER, TEST_VIDEOS_FOLDER, PROCESSED_FOLDER,
               EVIDENCE_FOLDER, DATABASE_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Video settings
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'}
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB

# Camera/Display settings
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
FPS_TARGET = 30

# Detection settings
ACCIDENT_THRESHOLD = 0.6
MIN_VEHICLES_FOR_ACCIDENT = 2
OVERLAP_THRESHOLD = 500

# Severity thresholds
SEVERITY_THRESHOLDS = {
    'MINOR': 30,
    'MAJOR': 60,
    'CRITICAL': 90
}

# Confidence thresholds
CONFIDENCE_LEVELS = {
    'HIGH': 85,
    'MEDIUM': 65,
    'LOW': 0
}

# Alert settings
ALERT_COOLDOWN = 5  # seconds between alerts
SAVE_EVIDENCE = True
MULTI_FRAME_CONFIRMATION = 3  # Confirm accident over multiple frames
DUPLICATE_ALERT_PREVENTION = True

# ===== COLORS =====
COLORS = {
    'MINOR': (0, 255, 255),     # Yellow
    'MAJOR': (0, 165, 255),     # Orange
    'CRITICAL': (0, 0, 255),    # Red
    'NORMAL': (0, 255, 0),      # Green
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'GRAY': (128, 128, 128),
    'HIGH_CONF': (0, 255, 0),   # Green
    'MED_CONF': (0, 255, 255),  # Yellow
    'LOW_CONF': (0, 0, 255)     # Red
}

# Performance metrics
TARGET_ACCURACY = 94.2
TARGET_RESPONSE_TIME = 1.3

# ANPR Settings
ANPR_ENABLED = True
ANPR_CONFIDENCE_THRESHOLD = 0.7

# Alert Settings
SMS_ENABLED = True
EMAIL_ENABLED = True
TELEGRAM_ENABLED = False
WHATSAPP_ENABLED = False
BUZZER_ENABLED = False

# Demo contacts
DEMO_PHONE_NUMBER = "+1234567890"
DEMO_EMAIL = "family@example.com"