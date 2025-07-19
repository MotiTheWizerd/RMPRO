import os
import json
import base64
import broadlink
import time
import uuid

class IRManager:
    def __init__(self, folder="signals"):
        self.folder = folder
        self.json_path = os.path.join(folder, "devices.json")
        os.makedirs(folder, exist_ok=True)
        self.device = None
        self.devices_cache = None  # Cache for devices data
        self.discover_and_auth()
        
    def discover_and_auth(self):
        """Discover and authenticate with the Broadlink device"""
        try:
            discovered_devices = broadlink.discover(timeout=5)
            if discovered_devices:
                self.device = discovered_devices[0]
                self.device.auth()
                return True, "Successfully authenticated with Broadlink device"
            else:
                return False, "No Broadlink devices found"
        except Exception as e:
            return False, f"Failed to discover or authenticate with Broadlink device: {e}"
    
    def get_devices(self):
        """Get all devices from cache or JSON file"""
        # Return cached devices if available
        if self.devices_cache is not None:
            return self.devices_cache
            
        # Otherwise load from file
        if not os.path.exists(self.json_path):
            self.devices_cache = []
            return []
        
        try:
            with open(self.json_path, "r") as f:
                self.devices_cache = json.load(f)
                return self.devices_cache
        except Exception:
            self.devices_cache = []
            return []
    
    def get_device(self, device_name):
        """Get a specific device by name"""
        devices = self.get_devices()
        for device in devices:
            if device["device_name"] == device_name:
                return device
        return None
    
    def get_device_by_id(self, device_id):
        """Get a specific device by ID"""
        devices = self.get_devices()
        for device in devices:
            if device.get("id") == device_id:
                return device
        return None
    
    def get_signal(self, device_name, signal_name):
        """Get a specific signal by device and signal name"""
        device = self.get_device(device_name)
        if not device:
            return None
            
        for signal in device["signals"]:
            if signal["signal_name"] == signal_name:
                return signal
        return None
    
    def get_signal_by_id(self, signal_id):
        """Get a specific signal by ID"""
        devices = self.get_devices()
        for device in devices:
            for signal in device.get("signals", []):
                if signal.get("id") == signal_id:
                    return signal, device
        return None, None
    
    def save_devices(self, devices_data):
        """Save devices data to JSON file and update cache"""
        # Update the cache
        self.devices_cache = devices_data
        
        # Save to file
        try:
            with open(self.json_path, "w") as f:
                json.dump(devices_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving devices: {e}")
            return False
            
    def create_device(self, device_name, device_description=""):
        """Create a new device without learning a signal"""
        # Load existing devices
        devices_data = self.get_devices()
        
        # Check if device already exists
        for device in devices_data:
            if device["device_name"] == device_name:
                return False, f"Device '{device_name}' already exists"
        
        # Add new device with UUID
        new_device = {
            "id": str(uuid.uuid4()),
            "device_name": device_name,
            "device_description": device_description,
            "signals": []
        }
        
        devices_data.append(new_device)
        
        # Save updated data
        if self.save_devices(devices_data):
            return True, f"Successfully created device '{device_name}'"
        else:
            return False, f"Failed to save device '{device_name}'"
    
    def add_test_signal(self, device_name, signal_name, signal_description=""):
        """Add a test signal to an existing device (for testing purposes)"""
        # Load existing devices
        devices_data = self.get_devices()
        
        # Find device
        device_found = False
        for device in devices_data:
            if device["device_name"] == device_name:
                device_found = True
                
                # Check if signal already exists
                for signal in device["signals"]:
                    if signal["signal_name"] == signal_name:
                        return False, f"Signal '{device_name}.{signal_name}' already exists"
                
                # Add new test signal with UUID
                device["signals"].append({
                    "id": str(uuid.uuid4()),
                    "signal_name": signal_name,
                    "signal_description": signal_description,
                    "signal_data": "JgBoAWJhYo4SNRMSETYRFBESEjUTNBMSEhMRExETEhITEhI1EjURFBESExISEhM1EhIRExI1EhMSEhITERITEhISExIRFBESEhMSNRI1EjUSNRMSERMSNhESEjUTEhISEhMRExISEhMSEhISEhMSEhITERMSEhISExISExE2ERITEhISExIRFBESExISEhITERMSEhITEhISEhISExISExETEhISEhMSEhMREhITEhITEhETEhISExISERQREhMSEhMSEhETEhITEhISEhMRExISEjUTEhETEjYREhITEjUSNRITETYRNhE2ERMSNRI1EhITNRI1EjUSEhITERMSEhITEhISEhITEjUSEhMSERMSEhITEhIRFBESExISEhMSERMSEhMSEhISExETEhISExETEhISEhMSEhMRExISEhITEhEUERISExISExIREhMSEhMSEhEUERITEhITETYRNhETEjYRNRI1EgANBQ=="  # Test signal data
                })
                
                # Save updated data
                if self.save_devices(devices_data):
                    return True, f"Successfully added test signal '{device_name}.{signal_name}'"
                else:
                    return False, f"Failed to save test signal '{device_name}.{signal_name}'"
                
        if not device_found:
            return False, f"Device '{device_name}' not found"
    
    def check_json_file(self):
        """Check if the JSON file exists and is valid"""
        if not os.path.exists(self.json_path):
            return False, f"JSON file '{self.json_path}' does not exist"
        
        try:
            with open(self.json_path, "r") as f:
                content = f.read()
                if not content.strip():
                    return False, f"JSON file '{self.json_path}' is empty"
                
                # Try to parse the JSON
                json.loads(content)
                return True, f"JSON file '{self.json_path}' is valid"
        except json.JSONDecodeError as e:
            return False, f"JSON file '{self.json_path}' contains invalid JSON: {e}"
        except Exception as e:
            return False, f"Error reading JSON file '{self.json_path}': {e}"
    
    def learn_signal(self, device_name, signal_name, signal_description="", device_description=""):
        """Learn and save an IR signal"""
        # Load existing devices
        devices_data = self.get_devices()
        
        # Find or create device
        device_found = False
        for device in devices_data:
            if device["device_name"] == device_name:
                device_found = True
                
                # Update device description if provided and current is empty
                if device_description and not device["device_description"]:
                    device["device_description"] = device_description
                
                break
        
        # Use the globally authenticated device if available
        if self.device is None:
            # If device is not available, try to discover and authenticate again
            success, message = self.discover_and_auth()
            if not success:
                return False, message
        
        # Enter learning mode
        try:
            self.device.enter_learning()
        except Exception as e:
            # If entering learning mode fails, try to rediscover and authenticate once
            try:
                success, message = self.discover_and_auth()
                if not success:
                    return False, message
                
                self.device.enter_learning()
            except Exception as e2:
                return False, f"Failed to enter learning mode: {e2}"
        
        # Wait for signal
        time.sleep(5)
        try:
            packet = self.device.check_data()
            # Convert binary packet to base64 string for JSON storage
            packet_base64 = base64.b64encode(packet).decode('utf-8')
        except OSError as e:
            if e.errno == -5:  # Storage full error
                return False, "Device storage is full. Try resetting your Broadlink device by unplugging it for 10 seconds, then plugging it back in."
            else:
                return False, f"Failed to capture signal: {e}"
        except Exception as e:
            return False, f"Failed to capture signal: {e}"
        
        # Add or update signal
        if device_found:
            # Find device in the list
            for device in devices_data:
                if device["device_name"] == device_name:
                    # Check if signal already exists
                    signal_found = False
                    for signal in device["signals"]:
                        if signal["signal_name"] == signal_name:
                            # Update existing signal
                            signal["signal_data"] = packet_base64
                            signal["signal_description"] = signal_description
                            signal_found = True
                            break
                    
                    # Add new signal if not found
                    if not signal_found:
                        device["signals"].append({
                            "id": str(uuid.uuid4()),
                            "signal_name": signal_name,
                            "signal_description": signal_description,
                            "signal_data": packet_base64
                        })
                    break
        else:
            # Add new device with UUID
            devices_data.append({
                "id": str(uuid.uuid4()),
                "device_name": device_name,
                "device_description": device_description,
                "signals": [{
                    "id": str(uuid.uuid4()),
                    "signal_name": signal_name,
                    "signal_description": signal_description,
                    "signal_data": packet_base64
                }]
            })
        
        # Save updated data
        self.save_devices(devices_data)
        return True, f"Successfully saved '{device_name}.{signal_name}'"
    
    def send_signal(self, device_name, signal_name):
        """Send an IR signal by device name and signal name"""
        # Get the signal
        signal = self.get_signal(device_name, signal_name)
        if not signal:
            return False, f"Signal '{device_name}.{signal_name}' not found"
        
        return self._send_signal_data(signal, f"'{device_name}.{signal_name}'")
    
    def send_signal_by_id(self, signal_id):
        """Send an IR signal by its UUID"""
        # Get the signal and device by ID
        signal, device = self.get_signal_by_id(signal_id)
        if not signal:
            return False, f"Signal with ID '{signal_id}' not found"
        
        device_name = device.get("device_name", "Unknown")
        signal_name = signal.get("signal_name", "Unknown")
        return self._send_signal_data(signal, f"'{device_name}.{signal_name}' (ID: {signal_id})")
    
    def _send_signal_data(self, signal, identifier):
        """Internal method to send signal data"""
        # Decode the signal
        try:
            binary_signal = base64.b64decode(signal["signal_data"])
        except Exception as e:
            return False, f"Error decoding signal: {e}"
        
        # Send the signal
        try:
            # Use the globally authenticated device if available
            if self.device is None:
                # If device is not available, try to discover and authenticate again
                success, message = self.discover_and_auth()
                if not success:
                    return False, message
            
            self.device.send_data(binary_signal)
            return True, f"Successfully sent {identifier}"
        except Exception as e:
            # If sending fails, try to rediscover and authenticate once
            try:
                success, message = self.discover_and_auth()
                if not success:
                    return False, message
                
                self.device.send_data(binary_signal)
                return True, f"Successfully sent {identifier}"
            except Exception as e2:
                return False, f"Error sending signal: {e2}"