import json
import os
import numpy as np
from datetime import datetime
from config import DATABASE_FOLDER


class Database:
    """
    Database manager with proper JSON handling
    """

    def __init__(self):
        self.vehicles_file = os.path.join(DATABASE_FOLDER, 'vehicles.json')
        self.accidents_file = os.path.join(DATABASE_FOLDER, 'accidents.json')
        self.alerts_file = os.path.join(DATABASE_FOLDER, 'alerts.json')

        self._init_database()
        print("✅ Database initialized")

    def _init_database(self):
        """Initialize database files with proper error handling"""
        # Create folder if not exists
        if not os.path.exists(DATABASE_FOLDER):
            os.makedirs(DATABASE_FOLDER)

        # Initialize each file
        for filepath in [self.vehicles_file, self.accidents_file, self.alerts_file]:
            if not os.path.exists(filepath):
                self._save_json(filepath, [])
            else:
                # Verify file is valid
                try:
                    self._load_json(filepath)
                except:
                    print(f"⚠️ Corrupted file detected: {os.path.basename(filepath)}")
                    print(f"   Creating new file...")
                    self._save_json(filepath, [])

    def _convert_to_serializable(self, obj):
        """Convert NumPy types to Python native types for JSON serialization"""
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, dict):
            return {key: self._convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    def _load_json(self, filepath):
        """Load JSON file with error handling"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:  # Empty file
                    return []
                return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON decode error in {os.path.basename(filepath)}: {e}")
            print(f"   Creating backup and resetting file...")

            # Backup corrupted file
            backup_file = filepath + ".corrupted"
            try:
                import shutil
                shutil.copy2(filepath, backup_file)
                print(f"   Backup saved to: {backup_file}")
            except:
                pass

            # Reset to empty list
            self._save_json(filepath, [])
            return []
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            return []

    def _save_json(self, filepath, data):
        """Save to JSON file with NumPy type conversion"""
        try:
            # Convert NumPy types to native Python types
            serializable_data = self._convert_to_serializable(data)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving to {os.path.basename(filepath)}: {e}")
            return False

    # Vehicle Management
    def add_vehicle(self, license_plate, owner_name, phone, email,
                    vehicle_model="", vehicle_color=""):
        """Add vehicle to database"""
        vehicles = self._load_json(self.vehicles_file)

        # Check if vehicle already exists
        for vehicle in vehicles:
            if vehicle.get('license_plate') == license_plate.upper():
                return False, "Vehicle already exists"

        vehicle_data = {
            'license_plate': license_plate.upper(),
            'owner_name': owner_name,
            'phone': phone,
            'email': email,
            'vehicle_model': vehicle_model,
            'vehicle_color': vehicle_color,
            'registered_date': datetime.now().isoformat(),
            'accident_history': [],
            'alert_history': []
        }

        vehicles.append(vehicle_data)
        success = self._save_json(self.vehicles_file, vehicles)

        if success:
            return True, "Vehicle added successfully"
        else:
            return False, "Failed to save vehicle"

    def get_vehicle(self, license_plate):
        """Get vehicle by license plate"""
        vehicles = self._load_json(self.vehicles_file)
        for vehicle in vehicles:
            if vehicle.get('license_plate') == license_plate.upper():
                return vehicle
        return None

    def update_vehicle(self, license_plate, updates):
        """Update vehicle information"""
        vehicles = self._load_json(self.vehicles_file)
        for i, vehicle in enumerate(vehicles):
            if vehicle.get('license_plate') == license_plate.upper():
                vehicles[i].update(updates)
                success = self._save_json(self.vehicles_file, vehicles)
                if success:
                    return True, "Vehicle updated"
                else:
                    return False, "Failed to update vehicle"
        return False, "Vehicle not found"

    def delete_vehicle(self, license_plate):
        """Delete vehicle from database"""
        vehicles = self._load_json(self.vehicles_file)
        original_count = len(vehicles)
        vehicles = [v for v in vehicles if v.get('license_plate') != license_plate.upper()]

        if len(vehicles) == original_count:
            return False, "Vehicle not found"

        success = self._save_json(self.vehicles_file, vehicles)
        if success:
            return True, "Vehicle deleted"
        else:
            return False, "Failed to delete vehicle"

    def get_all_vehicles(self):
        """Get all vehicles"""
        return self._load_json(self.vehicles_file)

    # Accident Management
    def log_accident(self, accident_data):
        """Log accident to database with proper error handling"""
        try:
            accidents = self._load_json(self.accidents_file)

            # Convert any NumPy types in accident_data
            serializable_data = self._convert_to_serializable(accident_data)

            # Add timestamp if not present
            if 'timestamp' not in serializable_data:
                serializable_data['timestamp'] = datetime.now().isoformat()

            accidents.append(serializable_data)

            # Keep only last 1000 accidents
            if len(accidents) > 1000:
                accidents = accidents[-1000:]

            success = self._save_json(self.accidents_file, accidents)

            # Update vehicle accident history if license plate exists
            if success and 'license_plate' in serializable_data and serializable_data['license_plate']:
                vehicles = self._load_json(self.vehicles_file)
                for vehicle in vehicles:
                    if vehicle.get('license_plate') == serializable_data['license_plate']:
                        if 'accident_history' not in vehicle:
                            vehicle['accident_history'] = []
                        vehicle['accident_history'].append(serializable_data)
                        self._save_json(self.vehicles_file, vehicles)
                        break

            return success

        except Exception as e:
            print(f"❌ Error logging accident: {e}")
            return False

    def get_accidents(self, limit=100, license_plate=None):
        """Get accident history"""
        accidents = self._load_json(self.accidents_file)

        if license_plate:
            accidents = [a for a in accidents if a.get('license_plate') == license_plate.upper()]

        return accidents[-limit:]

    # Alert Management
    def log_alert(self, alert_data):
        """Log alert to database"""
        try:
            alerts = self._load_json(self.alerts_file)

            # Convert NumPy types
            serializable_data = self._convert_to_serializable(alert_data)

            if 'timestamp' not in serializable_data:
                serializable_data['timestamp'] = datetime.now().isoformat()

            alerts.append(serializable_data)

            # Keep only last 1000 alerts
            if len(alerts) > 1000:
                alerts = alerts[-1000:]

            success = self._save_json(self.alerts_file, alerts)

            # Update vehicle alert history
            if success and 'license_plate' in serializable_data and serializable_data['license_plate']:
                vehicles = self._load_json(self.vehicles_file)
                for vehicle in vehicles:
                    if vehicle.get('license_plate') == serializable_data['license_plate']:
                        if 'alert_history' not in vehicle:
                            vehicle['alert_history'] = []
                        vehicle['alert_history'].append(serializable_data)
                        self._save_json(self.vehicles_file, vehicles)
                        break

            return success

        except Exception as e:
            print(f"❌ Error logging alert: {e}")
            return False

    def get_alerts(self, limit=100):
        """Get alert history"""
        return self._load_json(self.alerts_file)[-limit:]

    def clear_all_data(self):
        """Clear all database data"""
        self._save_json(self.vehicles_file, [])
        self._save_json(self.accidents_file, [])
        self._save_json(self.alerts_file, [])
        return True

    def get_statistics(self):
        """Get database statistics"""
        vehicles = self._load_json(self.vehicles_file)
        accidents = self._load_json(self.accidents_file)
        alerts = self._load_json(self.alerts_file)

        return {
            'total_vehicles': len(vehicles),
            'total_accidents': len(accidents),
            'total_alerts': len(alerts),
            'vehicles_with_accidents': len([v for v in vehicles if v.get('accident_history')])
        }