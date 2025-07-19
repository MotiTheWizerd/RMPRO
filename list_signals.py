#!/usr/bin/env python3
import os
import sys
import json

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
os.environ["PYTHONPATH"] = project_root

def main():
    """List all available signals in the system"""
    try:
        # Import the ir_manager module
        from ir_manager import IRManager
        
        # Create an instance of IRManager
        ir_manager = IRManager()
        
        # Get all devices
        devices = ir_manager.get_devices()
        
        if not devices:
            print("No devices found.")
            return
        
        print(f"Found {len(devices)} devices:")
        
        # Print all devices and their signals
        for device in devices:
            device_name = device.get("device_name", "Unknown")
            device_id = device.get("id", "No ID")
            signals = device.get("signals", [])
            
            print(f"\nDevice: {device_name} (ID: {device_id})")
            print(f"  Signals: {len(signals)}")
            
            for signal in signals:
                signal_name = signal.get("signal_name", "Unknown")
                signal_id = signal.get("id", "No ID")
                signal_desc = signal.get("signal_description", "")
                
                print(f"    - {signal_name} (ID: {signal_id})")
                if signal_desc:
                    print(f"      Description: {signal_desc}")
        
        # Export all signals to a JSON file for reference
        all_signals = []
        for device in devices:
            device_name = device.get("device_name", "Unknown")
            device_id = device.get("id", "No ID")
            
            for signal in device.get("signals", []):
                signal_name = signal.get("signal_name", "Unknown")
                signal_id = signal.get("id", "No ID")
                signal_desc = signal.get("signal_description", "")
                
                all_signals.append({
                    "device_name": device_name,
                    "device_id": device_id,
                    "signal_name": signal_name,
                    "signal_id": signal_id,
                    "signal_description": signal_desc
                })
        
        # Save to a JSON file
        with open("signals_list.json", "w") as f:
            json.dump(all_signals, f, indent=2)
        
        print(f"\nExported {len(all_signals)} signals to signals_list.json")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()