#!/usr/bin/env python3
import sys
import os

# Add the project root to the path so we can import ir_manager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from ir_manager import IRManager
from rich.console import Console
import sys
import json
import os

console = Console()

def send_signal_by_id(signal_id, silent=False):
    """Send an IR signal using its UUID
    
    Args:
        signal_id: The UUID of the signal to send
        silent: If True, don't print status messages
        
    Returns:
        bool: True if successful, False otherwise
    """
    ir_manager = IRManager()
    
    if not silent:
        with console.status(f"[bold blue]Sending signal with ID: {signal_id}...[/bold blue]"):
            success, message = ir_manager.send_signal_by_id(signal_id)
    else:
        success, message = ir_manager.send_signal_by_id(signal_id)
    
    if success:
        if not silent:
            console.print(f"[bold green]✅ {message}[/bold green]")
        return True
    else:
        if not silent:
            console.print(f"[bold red]❌ {message}[/bold red]")
        return False

def list_all_signals():
    """List all available signals with their IDs"""
    ir_manager = IRManager()
    devices = ir_manager.get_devices()
    
    if not devices:
        console.print("[bold yellow]No devices found.[/bold yellow]")
        return []
    
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
    
    return all_signals

def display_signals():
    """Display all signals with their IDs"""
    from rich.table import Table
    
    signals = list_all_signals()
    
    if not signals:
        return
    
    table = Table(title="Available Signals with IDs")
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Device", style="green")
    table.add_column("Signal", style="magenta")
    table.add_column("Description", style="blue")
    table.add_column("Signal ID", style="yellow")
    
    for i, signal in enumerate(signals, 1):
        table.add_row(
            f"[{i}]",
            signal["device_name"],
            signal["signal_name"],
            signal["signal_description"],
            signal["signal_id"]
        )
    
    console.print(table)

def export_signals_to_json(filename="signals_export.json"):
    """Export all signals to a JSON file for easy reference"""
    signals = list_all_signals()
    
    if not signals:
        console.print("[bold yellow]No signals to export.[/bold yellow]")
        return False
    
    try:
        with open(filename, "w") as f:
            json.dump(signals, f, indent=2)
        
        console.print(f"[bold green]✅ Successfully exported {len(signals)} signals to {filename}[/bold green]")
        return True
    except Exception as e:
        console.print(f"[bold red]❌ Failed to export signals: {e}[/bold red]")
        return False

def main():
    """Main function for command-line usage"""
    if len(sys.argv) == 1:
        # No arguments, display help
        console.print(Panel("""
[bold]Usage:[/bold]
  [green]python send_by_id.py list[/green]                # List all signals with their IDs
  [green]python send_by_id.py export [filename][/green]   # Export signals to JSON file
  [green]python send_by_id.py <signal_id>[/green]         # Send signal by ID
        """, title="Send Signal by ID"))
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        display_signals()
    elif command == "export":
        filename = sys.argv[2] if len(sys.argv) > 2 else "signals_export.json"
        export_signals_to_json(filename)
    else:
        # Assume the argument is a signal ID
        signal_id = command
        send_signal_by_id(signal_id)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Program terminated by user.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")