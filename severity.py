
import cv2
import numpy as np
from config import *


class SeverityClassifier:
    """Classifies accident severity"""

    def __init__(self):
        self.severity_levels = ['MINOR', 'MAJOR', 'CRITICAL']
        self.severity_history = []
        print("✅ Severity Classifier initialized")

    def classify(self, vehicles, motion, frame=None):
        """Classify accident severity"""
        if len(vehicles) < 2:
            return {
                'level': 'NONE',
                'score': 0,
                'confidence': 0,
                'factors': {}
            }

        factors = {}
        factors['vehicle_count'] = min(len(vehicles) * 10, 30)
        factors['overlap'] = self._calculate_overlap_score(vehicles)
        factors['motion'] = min(motion * 2, 20)

        if frame is not None:
            factors['debris'] = self._detect_debris(frame, vehicles)
        else:
            factors['debris'] = 0

        total_score = sum(factors.values())

        if total_score >= SEVERITY_THRESHOLDS['CRITICAL']:
            level = 'CRITICAL'
        elif total_score >= SEVERITY_THRESHOLDS['MAJOR']:
            level = 'MAJOR'
        else:
            level = 'MINOR'

        confidence = self._calculate_confidence(factors)

        return {
            'level': level,
            'score': total_score,
            'confidence': confidence,
            'factors': factors
        }

    def _calculate_overlap_score(self, vehicles):
        if len(vehicles) < 2:
            return 0
        return 15  # Simplified

    def _detect_debris(self, frame, vehicles):
        """Detect debris around accident area"""
        if frame is None or len(vehicles) < 2:
            return 0

        # Get accident area
        x1 = min(v['bbox'][0] for v in vehicles)
        y1 = min(v['bbox'][1] for v in vehicles)
        x2 = max(v['bbox'][2] for v in vehicles)
        y2 = max(v['bbox'][3] for v in vehicles)

        h, w = frame.shape[:2]
        x1 = max(0, x1 - 50)
        y1 = max(0, y1 - 50)
        x2 = min(w, x2 + 50)
        y2 = min(h, y2 + 50)

        roi = frame[y1:y2, x1:x2]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size
        edge_density = (edge_pixels / total_pixels) * 100 if total_pixels > 0 else 0

        return min(edge_density, 20)

    def _calculate_confidence(self, factors):
        values = list(factors.values())
        if not values:
            return 0
        std_dev = np.std(values)
        max_std = 50
        confidence = max(0, 100 - (std_dev / max_std) * 100)
        return min(confidence, 100)