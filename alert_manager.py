import time
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
from config import *


class AlertManager:
    """
    Alert Manager for:
    - SMS alerts
    - Email alerts
    - Telegram alerts
    - WhatsApp alerts
    - Buzzer alerts
    - Dashboard notifications
    """

    def __init__(self):
        self.alert_history = []
        self.last_alert_time = {}
        self.cooldown = ALERT_COOLDOWN

        # Email configuration (for demo)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "accident.detection.demo@gmail.com"
        self.sender_password = "demo_password"  # In production, use environment variables

        print("✅ Alert Manager initialized")

    def send_alert(self, vehicle_info, accident_data, severity_result,
                   image=None, location=None):
        """
        Send alerts to family contacts
        """
        license_plate = vehicle_info.get('license_plate', 'UNKNOWN')
        owner_name = vehicle_info.get('owner_name', 'Vehicle Owner')
        phone = vehicle_info.get('phone', DEMO_PHONE_NUMBER)
        email = vehicle_info.get('email', DEMO_EMAIL)

        # Check cooldown
        if DUPLICATE_ALERT_PREVENTION:
            last_time = self.last_alert_time.get(license_plate, 0)
            if time.time() - last_time < self.cooldown:
                print(f"⏸️ Alert cooldown active for {license_plate}")
                return False

        # Create alert message
        alert_message = self._create_alert_message(vehicle_info, accident_data,
                                                   severity_result, location)

        alerts_sent = []

        # Send SMS
        if SMS_ENABLED:
            success = self._send_sms(phone, alert_message)
            alerts_sent.append({'type': 'SMS', 'to': phone, 'success': success})

        # Send Email
        if EMAIL_ENABLED:
            success = self._send_email(email, alert_message, image, vehicle_info)
            alerts_sent.append({'type': 'Email', 'to': email, 'success': success})

        # Send Telegram
        if TELEGRAM_ENABLED:
            success = self._send_telegram(alert_message, image)
            alerts_sent.append({'type': 'Telegram', 'success': success})

        # Send WhatsApp
        if WHATSAPP_ENABLED:
            success = self._send_whatsapp(phone, alert_message)
            alerts_sent.append({'type': 'WhatsApp', 'to': phone, 'success': success})

        # Trigger Buzzer
        if BUZZER_ENABLED:
            self._trigger_buzzer(severity_result)
            alerts_sent.append({'type': 'Buzzer', 'success': True})

        # Log alert
        alert_log = {
            'timestamp': datetime.now().isoformat(),
            'license_plate': license_plate,
            'owner_name': owner_name,
            'severity': severity_result.get('level', 'UNKNOWN'),
            'alerts_sent': alerts_sent,
            'accident_data': accident_data
        }

        self.alert_history.append(alert_log)
        self.last_alert_time[license_plate] = time.time()

        # Display alert in console
        self._display_console_alert(alert_message, alerts_sent)

        return True

    def _create_alert_message(self, vehicle_info, accident_data, severity_result, location):
        """Create formatted alert message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        severity = severity_result.get('level', 'UNKNOWN')
        severity_score = severity_result.get('score', 0)
        confidence = accident_data.get('confidence', 0)

        # Severity emoji
        severity_emoji = {
            'MINOR': '⚠️',
            'MAJOR': '🔴',
            'CRITICAL': '🚨'
        }.get(severity, '⚠️')

        message = f"""
{severity_emoji} ACCIDENT DETECTED {severity_emoji}

Vehicle: {vehicle_info.get('license_plate', 'UNKNOWN')}
Owner: {vehicle_info.get('owner_name', 'Unknown')}
Model: {vehicle_info.get('vehicle_model', 'Unknown')}

⚠️ Severity: {severity} ({severity_score:.0f}%)
📊 Confidence: {confidence:.1f}%

📍 Location: {location or 'Camera Location'}

⏰ Time: {timestamp}

🚑 Emergency services have been notified.
Driver may be injured. Please respond immediately.
"""
        return message.strip()

    def _send_sms(self, phone, message):
        """Send SMS alert (simulated)"""
        print(f"\n📱 [SMS] To: {phone}")
        print(f"   Message: {message[:100]}...")
        print("   ✅ SMS sent (simulated)")
        return True

    def _send_email(self, email, message, image, vehicle_info):
        """Send email alert"""
        try:
            print(f"\n📧 [EMAIL] To: {email}")
            print(f"   Subject: ACCIDENT ALERT - {vehicle_info.get('license_plate')}")

            # Create email
            msg = MIMEMultipart()
            msg['Subject'] = f"🚨 ACCIDENT ALERT - {vehicle_info.get('license_plate', 'Unknown')}"
            msg['From'] = self.sender_email
            msg['To'] = email

            # Add message body
            msg.attach(MIMEText(message, 'plain'))

            # Attach image if available
            if image is not None:
                try:
                    from PIL import Image
                    import io

                    # Convert frame to image
                    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()

                    image_attachment = MIMEImage(img_byte_arr, name='accident_snapshot.jpg')
                    msg.attach(image_attachment)
                except:
                    pass

            # In production, uncomment to send actual email
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.sender_email, self.sender_password)
            # server.send_message(msg)
            # server.quit()

            print("   ✅ Email sent (simulated)")
            return True

        except Exception as e:
            print(f"   ❌ Email error: {e}")
            return False

    def _send_telegram(self, message, image):
        """Send Telegram alert"""
        print(f"\n📱 [TELEGRAM] Alert sent")
        print("   ✅ Telegram alert (simulated)")
        return True

    def _send_whatsapp(self, phone, message):
        """Send WhatsApp alert"""
        print(f"\n💬 [WHATSAPP] To: {phone}")
        print("   ✅ WhatsApp alert (simulated)")
        return True

    def _trigger_buzzer(self, severity_result):
        """Trigger buzzer alert"""
        severity = severity_result.get('level', 'MINOR')
        duration = 3 if severity == 'CRITICAL' else 1

        print(f"\n🔊 [BUZZER] Triggered for {duration} seconds")
        # In production, use GPIO to trigger buzzer
        return True

    def _display_console_alert(self, message, alerts_sent):
        """Display alert in console"""
        print("\n" + "=" * 70)
        print("🚨 FAMILY ALERT SYSTEM - NOTIFICATIONS SENT")
        print("=" * 70)
        print(message)
        print("\n📢 Alert Delivery Status:")
        for alert in alerts_sent:
            status = "✅" if alert['success'] else "❌"
            print(f"   {status} {alert['type']}: {alert.get('to', 'N/A')}")
        print("=" * 70)

    def get_alert_history(self, limit=50):
        """Get alert history"""
        return self.alert_history[-limit:]

    def get_statistics(self):
        """Get alert statistics"""
        total_alerts = len(self.alert_history)
        if total_alerts == 0:
            return {'total_alerts': 0}

        severity_counts = {'MINOR': 0, 'MAJOR': 0, 'CRITICAL': 0}
        for alert in self.alert_history:
            severity = alert.get('severity', 'MINOR')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            'total_alerts': total_alerts,
            'severity_breakdown': severity_counts,
            'last_alert': self.alert_history[-1] if self.alert_history else None
        }