
import cv2
import numpy as np
import math
from config import COLORS


class ImpactVisualizer:
    def __init__(self):
        self.heatmap_intensity = 0.0
        self.impact_points = []
        print("✅ Impact Visualizer initialized")

    def draw_heatmap(self, frame, vehicles, severity_score):
        h, w = frame.shape[:2]
        heatmap = np.zeros((h, w), dtype=np.float32)
        self.heatmap_intensity = min(severity_score / 100, 1.0)

        for vehicle in vehicles:
            x1, y1, x2, y2 = vehicle['bbox']
            center = ((x1 + x2) // 2, (y1 + y2) // 2)
            intensity = vehicle.get('confidence', 0.5) * self.heatmap_intensity
            radius = min(abs(x2 - x1), abs(y2 - y1)) // 2
            self._add_gaussian_spot(heatmap, center, radius, intensity)

        if np.max(heatmap) > 0:
            heatmap = heatmap / np.max(heatmap)

        heatmap_colored = self._apply_colormap(heatmap)
        alpha = 0.6
        blended = cv2.addWeighted(frame, 1 - alpha, heatmap_colored, alpha, 0)
        blended = self._add_direction_arrows(blended, vehicles)

        return blended

    def _add_gaussian_spot(self, heatmap, center, radius, intensity):
        h, w = heatmap.shape
        cx, cy = center
        y, x = np.ogrid[:h, :w]
        distance = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        sigma = max(radius / 3, 1)
        mask = np.exp(-(distance ** 2) / (2 * sigma ** 2))
        mask[distance > radius * 2] = 0
        heatmap += mask * intensity

    def _apply_colormap(self, heatmap):
        h, w = heatmap.shape
        colored = np.zeros((h, w, 3), dtype=np.uint8)
        heatmap_255 = (heatmap * 255).astype(np.uint8)
        colored[:, :, 0] = np.clip(255 - heatmap_255 * 2, 0, 255).astype(np.uint8)
        green = np.clip(255 - np.abs(heatmap_255 - 128) * 2, 0, 255)
        colored[:, :, 1] = green.astype(np.uint8)
        colored[:, :, 2] = heatmap_255
        return colored

    def _add_direction_arrows(self, frame, vehicles):
        if len(vehicles) < 2:
            return frame

        centers = [v['center'] for v in vehicles]
        for i in range(len(centers)):
            for j in range(i + 1, len(centers)):
                pt1 = centers[i]
                pt2 = centers[j]
                dist = math.sqrt((pt2[0] - pt1[0]) ** 2 + (pt2[1] - pt1[1]) ** 2)
                if dist < 200:
                    cv2.arrowedLine(frame, pt1, pt2, COLORS['CRITICAL'], 2, tipLength=0.2)
        return frame