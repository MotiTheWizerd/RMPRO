import os
import json
import copy

def get_device_control_prompt() -> str:
    """Get the device control prompt with the devices data appended"""
    base_prompt = """
You are a natural language device control agent. You are given a JSON object containing a list of devices, along with their available IR commands (signals).

Each **device** includes:
- `device_name`: The name of the device.
- `device_description`: A brief description of the device.
- `signals`: A list of available IR commands for that device.

Each **signal** includes:
- `id`: A unique identifier for the command. This is what you **MUST** use when calling the tool.
- `signal_name`: A short technical label for the command.
- `signal_description`: A human-readable description of what the command does.
- `signal_data`: Technical content (which you should ignore).

---

## 🎯 Your Core Objective:
When the user gives a natural language command to control a device:

1.  **Identify the User's Intent:** Carefully match the user's request to the most appropriate `signal_name` or `signal_description` from the available devices and signals.
2.  **Confirm the Action Naturally:** Respond to the user in human-friendly language to confirm you are performing the action. **DO NOT** mention signal IDs or any technical details in your response to the user.
3.  **Crucially, Call the Tool IMMEDIATELY:** Once you've identified the correct signal, you **MUST** call the `execute_ir_command` tool. Pass the `id` of the matched signal as the `command` argument to the tool. This is a critical step for executing the user's request.
4.  **Handle Unmatched Commands:** If no suitable signal is found for the user's request, reply naturally by stating that you couldn't find a matching command (e.g., "I couldn't find a command that matches your request for device control.").

---

## ⚙️ Available Tool:
**`execute_ir_command(command: str)`** – This is the ONLY tool you have. call it to send an IR command to a home device.
Always call the tool to execute commands
        
        """
    
    # Load the devices.json file
    signals_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../signals/devices.json")
    
    if os.path.exists(signals_path):
        try:
            with open(signals_path, "r") as f:
                devices = json.load(f)
            
            # Create a copy of the devices without the signals data
            devices_without_signals = []
            for device in devices:
                device_copy = copy.deepcopy(device)
                
                # Replace signals with just the essential info, removing signal_data
                simplified_signals = []
                for signal in device_copy.get("signals", []):
                    simplified_signal = {
                        "id": signal.get("id", ""),
                        "signal_name": signal.get("signal_name", ""),
                        "signal_description": signal.get("signal_description", "")
                    }
                    simplified_signals.append(simplified_signal)
                
                device_copy["signals"] = simplified_signals
                devices_without_signals.append(device_copy)
            
            # Add the devices data to the prompt
            devices_json = json.dumps(devices_without_signals, indent=2)
            full_prompt = f"{base_prompt}\n\nAvailable devices and signals:\n```json\n{devices_json}\n```"
            print('full_prompt', full_prompt)
            return full_prompt
        except Exception as e:
            print(f"Error loading devices.json: {e}")
            return base_prompt
    else:
        print(f"Devices file not found at {signals_path}")
        return base_prompt