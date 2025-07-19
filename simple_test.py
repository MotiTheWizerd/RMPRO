#!/usr/bin/env python3
import os
import sys
import json

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import the necessary modules
from agents.device_control_agent.utils.execute_ir_command_tool import execute_ir_command

def main():
    """Simple test for execute_ir_command"""
    print("Testing execute_ir_command...")
    
    # Test with a search term for multiple matches
    print("\nTesting with search term 'tv':")
    result = execute_ir_command("tv")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if "matches" in result and result["matches"]:
        print(f"Found {len(result['matches'])} matches:")
        for i, match in enumerate(result["matches"], 1):
            print(f"  {i}. {match['device_name']}.{match['signal_name']} - {match['signal_description']}")
    
    # Test with a search term for a single match
    print("\nTesting with search term 'ac':")
    result = execute_ir_command("ac")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if "signal" in result:
        signal = result["signal"]
        print(f"Signal: {signal['device_name']}.{signal['signal_name']} - {signal['signal_description']}")
    
    # Test with a real signal ID
    real_id = "0d71bc16-0327-4789-9e1d-5aa7d0def2ad"
    print(f"\nTesting with real signal ID {real_id}:")
    result = execute_ir_command(real_id)
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    if "signal" in result:
        signal = result["signal"]
        print(f"Signal: {signal['device_name']}.{signal['signal_name']} - {signal['signal_description']}")
    
    # Test with an invalid search term
    print("\nTesting with invalid search term 'xyz':")
    result = execute_ir_command("xyz")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")

if __name__ == "__main__":
    main()