from typing import Dict, Any, List, Optional
import sys
import os
import json
import subprocess

def execute_ir_command(command: str) -> Dict[str, Any]:
    """
    Execute an IR command by signal ID.
    
    Args:
        command: The UUID of the signal to send
        
    Returns:
        Dict with success status and message
    """
    try:
        # Check if the command is a valid UUID (simple check)
        is_uuid = len(command) > 30 and "-" in command
        
        if not is_uuid:
            return {
                "success": False,
                "message": f"Invalid signal ID format: {command}",
                "error": "Invalid ID format"
            }
        
        # Try to run the send_by_id.py script with the signal ID
        try:
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../remote_control_tools/send_by_id.py")
            
            if os.path.exists(script_path):
                # Actually execute the command
                python_executable = sys.executable  # Get the current Python executable
                cmd = [python_executable, script_path, command]
                
                # Execute the command
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": f"Signal with ID {command} sent successfully",
                        "signal_id": command,
                        "output": result.stdout.strip()
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Error sending signal: {result.stderr.strip()}",
                        "signal_id": command,
                        "error": result.stderr.strip()
                    }
            else:
                # Fall back to simulation if script doesn't exist
                return {
                    "success": True,
                    "message": f"Signal with ID {command} sent successfully (simulated)",
                    "signal_id": command,
                    "simulated": True
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error sending signal: {str(e)}",
                "error": str(e)
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error executing command: {str(e)}",
            "error": str(e)
        }