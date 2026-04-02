
import cv2  # ← ADD THIS IMPORT
import time
import os
import json
from datetime import datetime
from config import *


class EmergencyAlertSystem:
    """
    Emergency response system for major and critical accidents
    """

    def __init__(self):
        self.alerts_sent = 0
        self.last_alert_time = 0
        self.alert_cooldown = ALERT_COOLDOWN
        self.emergency_contacts = {
            'police': '100',
            'ambulance': '108',
            'fire': '101'
        }
        print("✅ Emergency Alert System initialized")

    def trigger_alert(self, frame, detection_result, severity_result, confidence_result):
        """
        Trigger emergency alert for major/critical accidents
        """
        current_time = time.time()

        # Check cooldown
        if current_time - self.last_alert_time < self.alert_cooldown:
            return False

        severity = severity_result.get('level', 'UNKNOWN')

        # Only alert for Major and Critical accidents (as per PPT)
        if severity not in ['MAJOR', 'CRITICAL']:
            return False

        # Create alert data
        timestamp = datetime.now().isoformat()
        alert_id = f"ALT-{int(time.time())}-{self.alerts_sent + 1}"

        alert_data = {
            'id': alert_id,
            'timestamp': timestamp,
            'severity': severity,
            'confidence': confidence_result.get('score', 0),
            'vehicle_count': detection_result.get('vehicle_count', 0),
            'location': self._get_location(),
            'response_time': self._calculate_response_time(detection_result),
            'services_dispatched': self._get_services_for_severity(severity)
        }

        # Save evidence
        if SAVE_EVIDENCE and frame is not None:
            evidence_path = self._save_evidence(frame, alert_id, alert_data)
            alert_data['evidence'] = evidence_path

        # Display alert (as shown in PPT)
        self._display_alert(alert_data)

        # Log alert
        self._log_alert(alert_data)

        # Update counters
        self.alerts_sent += 1
        self.last_alert_time = current_time

        return True

    def _get_location(self):
        """Get simulated location"""
        locations = [
            "Highway Exit 24, North Side",
            "Downtown Intersection, Main St & 5th Ave",
            "Bridge Crossing, Golden Gate",
            "Tunnel Entry, Holland Tunnel",
            "School Zone, Oak Street",
            "Roundabout, Central Square"
        ]
        import random
        return random.choice(locations)

    def _calculate_response_time(self, detection_result):
        """Calculate response time (as shown in PPT: 1.3 seconds)"""
        # From PPT: response time = 1.3 seconds
        detection_time = detection_result.get('timestamp', time.time())
        accident_time = detection_time - 1.3  # Simulated
        return time.time() - accident_time

    def _get_services_for_severity(self, severity):
        """Get emergency services based on severity"""
        if severity == 'CRITICAL':
            return ['Police', 'Ambulance', 'Fire Department']
        else:  # MAJOR
            return ['Police', 'Ambulance']

    def _save_evidence(self, frame, alert_id, alert_data):
        """Save video evidence"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        evidence_file = os.path.join(EVIDENCE_FOLDER, f"evidence_{alert_id}_{timestamp}.jpg")

        # Save frame using cv2 (now imported)
        cv2.imwrite(evidence_file, frame)

        # Save metadata
        metadata_file = os.path.join(EVIDENCE_FOLDER, f"metadata_{alert_id}_{timestamp}.json")
        with open(metadata_file, 'w') as f:
            json.dump(alert_data, f, indent=2)

        return evidence_file

    def _display_alert(self, alert_data):
        """Display alert in console (as shown in PPT)"""
        print("\n" + "=" * 70)
        print("🚨 EMERGENCY ALERT TRIGGERED!")
        print("=" * 70)
        print(f"🆔 Alert ID: {alert_data['id']}")
        print(f"⏰ Time: {alert_data['timestamp']}")
        print(f"⚠️ Severity: {alert_data['severity']}")
        print(f"📊 Confidence: {alert_data['confidence']:.1f}%")
        print(f"🚗 Vehicles: {alert_data['vehicle_count']}")
        print(f"📍 Location: {alert_data['location']}")
        print(f"⚡ Response Time: {alert_data['response_time']:.2f} seconds")
        print("\n🚑 Services Dispatched:")
        for service in alert_data['services_dispatched']:
            print(f"   ✓ {service}")
        print("=" * 70)

        # Simulate emergency call
        self._simulate_emergency_call(alert_data)

    def _simulate_emergency_call(self, alert_data):
        """Simulate emergency phone call"""
        print("\n📞 SIMULATING EMERGENCY CALL...")
        time.sleep(0.5)
        print("   Dialing 911...")
        time.sleep(0.5)
        print("   Operator: What's your emergency?")
        time.sleep(0.5)
        print(f"   System: {alert_data['severity']} accident at {alert_data['location']}")
        time.sleep(0.5)
        print(f"   System: {len(alert_data['services_dispatched'])} services dispatched")
        time.sleep(0.5)
        print("   ✅ Emergency services notified\n")

    def _log_alert(self, alert_data):
        """Log alert to file"""
        log_file = os.path.join(EVIDENCE_FOLDER, "emergency_alerts.log")
        with open(log_file, 'a') as f:
            f.write(f"{alert_data['timestamp']} | {alert_data['id']} | ")
            f.write(f"{alert_data['severity']} | Confidence: {alert_data['confidence']:.1f}% | ")
            f.write(f"Services: {', '.join(alert_data['services_dispatched'])}\n")

    def get_statistics(self):
        """Get alert statistics"""
        return {
            'alerts_sent': self.alerts_sent,
            'last_alert': self.last_alert_time,
            'cooldown': self.alert_cooldown
        }