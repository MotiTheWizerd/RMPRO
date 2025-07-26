from typing import Dict, Any, List, Optional
import sys
import os
import json
import subprocess

def execute_ir_command(command: str) -> Dict[str, Any]:
    print('=== DEBUG: execute_ir_command called ===')
    print(f'Command received: {command}')
    print(f'Current working directory: {os.getcwd()}')
    print(f'Python executable: {sys.executable}')
    print('Environment variables:')
    for key in ['PATH', 'PYTHONPATH', 'VIRTUAL_ENV']:
        print(f'  {key}: {os.environ.get(key, "Not set")}')
    print('======================================')
    
    # Try to list installed packages for debugging
    try:
        import pkg_resources
        print('\nInstalled packages:')
        for d in pkg_resources.working_set:
            print(f'  {d.project_name}=={d.version}')
    except Exception as e:
        print(f'\nCould not list installed packages: {e}')
    
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
            # Try multiple possible paths to find send_by_id.py
            possible_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../remote_control_tools/send_by_id.py"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../remote_control_tools/send_by_id.py"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "remote_control_tools/send_by_id.py"),
                os.path.abspath("remote_control_tools/send_by_id.py"),
                "remote_control_tools/send_by_id.py"
            ]
            
            script_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    script_path = os.path.abspath(path)
                    print(f"[DEBUG] Found send_by_id.py at: {script_path}")
                    break
            
            if script_path and os.path.exists(script_path):
                # Actually execute the command
                python_executable = sys.executable  # Get the current Python executable
                cmd = [python_executable, script_path, command]
                print(f"[DEBUG] Using command: {' '.join(cmd)}")
                
                # Execute the command with full output capture
                print(f"[DEBUG] Running command: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # Debug output
                print(f"[DEBUG] Return code: {result.returncode}")
                print(f"[DEBUG] stdout: {result.stdout}")
                print(f"[DEBUG] stderr: {result.stderr}")
                
                if result.returncode == 0:
                    response = {
                        "success": True,
                        "message": f"Signal with ID {command} sent successfully",
                        "signal_id": command,
                        "output": result.stdout.strip()
                    }
                    print(f"[SUCCESS] {response}")
                    return response
                else:
                    error_msg = f"Error sending signal (code {result.returncode}): {result.stderr.strip()}"
                    print(f"[ERROR] {error_msg}")
                    return {
                        "success": False,
                        "message": error_msg,
                        "signal_id": command,
                        "error": result.stderr.strip(),
                        "exit_code": result.returncode
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
