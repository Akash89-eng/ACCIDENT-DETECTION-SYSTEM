
import cv2
import time
import numpy as np
from datetime import datetime
from config import *


class LiveDashboard:
    """
    Live dashboard showing:
    - Real-time vehicle count
    - Accident detection status
    - System performance
    - Detection trends
    - Controls
    """

    def __init__(self):
        self.metrics_history = []
        self.start_time = time.time()
        self.frame_count = 0
        print("✅ Live Dashboard initialized")

    def draw(self, frame, detection_result, severity_result, confidence_result, performance):
        """
        Draw live dashboard on frame
        """
        h, w = frame.shape[:2]

        # Draw semi-transparent sidebar
        sidebar_width = 350
        self._draw_sidebar(frame, sidebar_width, h)

        # Add dashboard content
        x_offset = w - sidebar_width + 20
        y_offset = 50

        # Title
        cv2.putText(frame, "LIVE DASHBOARD", (x_offset, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['WHITE'], 2)
        y_offset += 40

        # 1. Vehicle Count
        cv2.putText(frame, "🚗 VEHICLES", (x_offset, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['GRAY'], 1)
        y_offset += 25
        vehicle_count = detection_result.get('vehicle_count', 0)
        cv2.putText(frame, str(vehicle_count), (x_offset + 20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['WHITE'], 2)
        y_offset += 40

        # 2. Accident Status
        cv2.putText(frame, "⚠️ ACCIDENT STATUS", (x_offset, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['GRAY'], 1)
        y_offset += 25

        if detection_result.get('accident_detected', False):
            severity = severity_result.get('level', 'UNKNOWN')
            color = self._get_severity_color(severity)
            cv2.putText(frame, f"ACTIVE - {severity}", (x_offset + 20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        else:
            cv2.putText(frame, "NORMAL", (x_offset + 20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLORS['NORMAL'], 2)
        y_offset += 40

        # 3. Severity Level
        if detection_result.get('accident_detected', False):
            cv2.putText(frame, "📊 SEVERITY", (x_offset, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['GRAY'], 1)
            y_offset += 25

            severity_score = severity_result.get('score', 0)
            self._draw_progress_bar(frame, x_offset, y_offset, severity_score, 200, 20)
            y_offset += 35

            cv2.putText(frame, f"{severity_score:.1f}%", (x_offset + 210, y_offset - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['WHITE'], 1)
        y_offset += 20

        # 4. Confidence Score
        cv2.putText(frame, "🎯 CONFIDENCE", (x_offset, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['GRAY'], 1)
        y_offset += 25

        confidence_score = confidence_result.get('score', 0)
        confidence_level = confidence_result.get('level', 'LOW')
        confidence_color = confidence_result.get('color', COLORS['LOW_CONF'])

        self._draw_progress_bar(frame, x_offset, y_offset, confidence_score, 200, 20, confidence_color)
        y_offset += 35

        cv2.putText(frame, f"{confidence_score:.1f}%", (x_offset + 210, y_offset - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['WHITE'], 1)
        cv2.putText(frame, confidence_level, (x_offset + 210, y_offset - 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, confidence_color, 1)
        y_offset += 30

        # 5. Performance Metrics
        cv2.putText(frame, "⚡ PERFORMANCE", (x_offset, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['GRAY'], 1)
        y_offset += 25

        # FPS
        fps = performance.get('fps', 0)
        cv2.putText(frame, f"FPS: {fps:.1f}", (x_offset + 20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['WHITE'], 1)
        y_offset += 25

        # Processing time
        proc_time = performance.get('process_time', 0) * 1000
        cv2.putText(frame, f"Process: {proc_time:.1f}ms", (x_offset + 20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['WHITE'], 1)
        y_offset += 25

        # Frame count
        frame_num = performance.get('frame', 0)
        cv2.putText(frame, f"Frame: {frame_num}", (x_offset + 20, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['WHITE'], 1)
        y_offset += 35

        # 6. Detection Trend (mini graph)
        if len(self.metrics_history) > 1:
            cv2.putText(frame, "📈 DETECTION TREND", (x_offset, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['GRAY'], 1)
            y_offset += 30
            self._draw_trend_graph(frame, x_offset, y_offset, 200, 50)
            y_offset += 60

        # 7. Controls
        cv2.putText(frame, "🎮 CONTROLS", (x_offset, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['GRAY'], 1)
        y_offset += 25

        controls = [
            ("[Q]", "Quit"),
            ("[P]", "Pause"),
            ("[H]", "Heatmap"),
            ("[S]", "Screenshot"),
            ("[1-3]", "Demo Accidents")
        ]

        for key, action in controls:
            cv2.putText(frame, f"{key} {action}", (x_offset + 20, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['GRAY'], 1)
            y_offset += 20

        # Update metrics history
        self.metrics_history.append({
            'time': time.time(),
            'confidence': confidence_score,
            'detected': detection_result.get('accident_detected', False)
        })
        if len(self.metrics_history) > 50:
            self.metrics_history.pop(0)

        return frame

    def _draw_sidebar(self, frame, width, height):
        """Draw semi-transparent sidebar"""
        overlay = frame.copy()
        cv2.rectangle(overlay, (frame.shape[1] - width, 0), (frame.shape[1], height),
                      (30, 30, 40), -1)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # Sidebar border
        cv2.line(frame, (frame.shape[1] - width, 0), (frame.shape[1] - width, height),
                 (100, 100, 100), 1)

    def _draw_progress_bar(self, frame, x, y, value, width, height, color=COLORS['WHITE']):
        """Draw progress bar"""
        # Background
        cv2.rectangle(frame, (x, y), (x + width, y + height), (50, 50, 50), -1)

        # Fill
        fill_width = int(width * value / 100)
        cv2.rectangle(frame, (x, y), (x + fill_width, y + height), color, -1)

        # Border
        cv2.rectangle(frame, (x, y), (x + width, y + height), (200, 200, 200), 1)

    def _draw_trend_graph(self, frame, x, y, width, height):
        """Draw mini trend graph"""
        if len(self.metrics_history) < 2:
            return

        # Graph background
        cv2.rectangle(frame, (x, y), (x + width, y + height), (20, 20, 20), -1)

        # Draw grid lines
        for i in range(0, width, 20):
            cv2.line(frame, (x + i, y), (x + i, y + height), (40, 40, 40), 1)
        for i in range(0, height, 10):
            cv2.line(frame, (x, y + i), (x + width, y + i), (40, 40, 40), 1)

        # Draw confidence trend
        points = []
        recent = self.metrics_history[-20:]

        for i, metric in enumerate(recent):
            graph_x = x + int(i * width / len(recent))
            conf = metric.get('confidence', 0)
            graph_y = y + height - int(conf * height / 100)
            points.append((graph_x, graph_y))

        # Draw lines
        for i in range(1, len(points)):
            cv2.line(frame, points[i - 1], points[i], COLORS['WHITE'], 1)

    def _get_severity_color(self, severity):
        """Get color for severity level"""
        colors = {
            'MINOR': COLORS['MINOR'],
            'MAJOR': COLORS['MAJOR'],
            'CRITICAL': COLORS['CRITICAL']
        }
        return colors.get(severity, COLORS['WHITE'])