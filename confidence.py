import numpy as np
from config import *


class ConfidenceScorer:
    """
    Calculates confidence scores with three levels:
    - HIGH (>85%) - Green
    - MEDIUM (65-85%) - Yellow
    - LOW (<65%) - Red
    """

    def __init__(self):
        self.confidence_history = []
        print("✅ Confidence Scorer initialized")

    def calculate(self, detection_result, severity_result, metrics=None):
        """
        Calculate confidence score based on multiple factors
        Returns: confidence score, level, color, factors
        """
        factors = {}

        # Factor 1: Detection confidence (0-40)
        factors['detection'] = detection_result.get('confidence', 0) * 40

        # Factor 2: Severity confidence (0-30)
        factors['severity'] = severity_result.get('confidence', 0) * 0.3

        # Factor 3: Temporal consistency (0-20)
        factors['temporal'] = self._calculate_temporal_consistency(detection_result)

        # Factor 4: Scene context (0-10)
        factors['scene'] = self._calculate_scene_context(detection_result)

        # Calculate total confidence (0-100)
        total_confidence = sum(factors.values())

        # Determine confidence level
        level, color = self._get_confidence_level(total_confidence)

        result = {
            'score': total_confidence,
            'level': level,
            'color': color,
            'factors': factors
        }

        self.confidence_history.append(total_confidence)
        return result

    def _calculate_temporal_consistency(self, detection_result):
        """Check consistency over time"""
        if len(self.confidence_history) < 5:
            return 15  # Default

        # Check if recent detections agree
        recent = self.confidence_history[-5:]
        variance = np.var(recent)

        # Lower variance = higher consistency
        if variance < 100:
            return 20
        elif variance < 500:
            return 15
        else:
            return 5

    def _calculate_scene_context(self, detection_result):
        """Check if scene makes sense"""
        vehicle_count = detection_result.get('vehicle_count', 0)

        # More vehicles = more confidence
        if vehicle_count >= 4:
            return 10
        elif vehicle_count >= 2:
            return 7
        else:
            return 3

    def _get_confidence_level(self, score):
        """Get confidence level and color"""
        if score >= CONFIDENCE_LEVELS['HIGH']:
            return 'HIGH', COLORS['HIGH_CONF']
        elif score >= CONFIDENCE_LEVELS['MEDIUM']:
            return 'MEDIUM', COLORS['MED_CONF']
        else:
            return 'LOW', COLORS['LOW_CONF']

    def get_confidence_bar(self, score, width=200, height=20):
        """Generate confidence bar visualization"""
        bar = np.zeros((height, width, 3), dtype=np.uint8)

        # Background
        bar[:, :] = (50, 50, 50)

        # Fill based on confidence
        fill_width = int(width * score / 100)
        color = self._get_confidence_level(score)[1]
        bar[:, :fill_width] = color

        return bar