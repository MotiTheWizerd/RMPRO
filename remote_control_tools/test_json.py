#!/usr/bin/env python3
from ir_manager import IRManager
from rich.console import Console

console = Console()

def test_json_operations():
    """Test JSON file operations"""
    console.print("[bold blue]Testing JSON File Operations[/bold blue]")
    
    # Create IR Manager
    ir_manager = IRManager()
    
    # Check if JSON file exists and is valid
    console.print("\n[bold]Checking JSON file...[/bold]")
    success, message = ir_manager.check_json_file()
    if success:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[yellow]⚠️ {message}[/yellow]")
    
    # Create a test device
    console.print("\n[bold]Creating test device...[/bold]")
    success, message = ir_manager.create_device("test_device", "Test Device Description")
    if success:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[red]❌ {message}[/red]")
    
    # Check JSON file again
    console.print("\n[bold]Checking JSON file after device creation...[/bold]")
    success, message = ir_manager.check_json_file()
    if success:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[yellow]⚠️ {message}[/yellow]")
    
    # Add a test signal
    console.print("\n[bold]Adding test signal...[/bold]")
    success, message = ir_manager.add_test_signal("test_device", "test_signal", "Test Signal Description")
    if success:
        console.print(f"[green]✅ {message}[/green]")
    else:
        console.print(f"[red]❌ {message}[/red]")
    
    # Check devices in memory
    console.print("\n[bold]Checking devices in memory...[/bold]")
    devices = ir_manager.get_devices()
    console.print(f"Number of devices: {len(devices)}")
    for device in devices:
        console.print(f"Device: {device['device_name']}")
        console.print(f"  ID: {device.get('id', 'No ID')}")
        console.print(f"  Description: {device.get('device_description', 'No description')}")
        console.print(f"  Signals: {len(device.get('signals', []))}")
        for signal in device.get('signals', []):
            console.print(f"    - {signal['signal_name']} (ID: {signal.get('id', 'No ID')})")
    
    # Try to read the file directly
    console.print("\n[bold]Reading JSON file directly...[/bold]")
    try:
        with open(ir_manager.json_path, "r") as f:
            content = f.read()
            console.print(f"File size: {len(content)} bytes")
            if content.strip():
                console.print("[green]File is not empty[/green]")
            else:
                console.print("[red]File is empty[/red]")
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")

if __name__ == "__main__":
    test_json_operations()