from ir_manager import IRManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich import print as rprint
import sys

console = Console()

def display_devices_and_signals(devices):
    """Display all devices and their signals in a rich table"""
    if not devices:
        console.print(Panel("[yellow]No devices found[/yellow]", title="Devices"))
        return
    
    table = Table(title="Available Devices and Signals")
    table.add_column("Device #", style="cyan", justify="right")
    table.add_column("Device Name", style="green")
    table.add_column("Signal #", style="cyan", justify="right")
    table.add_column("Signal Name", style="magenta")
    table.add_column("Description", style="blue")
    
    for i, device in enumerate(devices, 1):
        # If device has no signals, show just the device
        if not device.get("signals"):
            table.add_row(
                f"[{i}]", 
                device["device_name"], 
                "", 
                "[italic]No signals[/italic]",
                device.get("device_description", "")
            )
            continue
            
        # First row shows device with its first signal
        first_signal = device["signals"][0]
        table.add_row(
            f"[{i}]", 
            device["device_name"], 
            f"[{i}.1]", 
            first_signal["signal_name"],
            first_signal.get("signal_description", "")
        )
        
        # Remaining signals for this device
        for j, signal in enumerate(device["signals"][1:], 2):
            table.add_row(
                "", 
                "", 
                f"[{i}.{j}]", 
                signal["signal_name"],
                signal.get("signal_description", "")
            )
    
    console.print(table)

def interactive_mode():
    """Interactive mode for sending signals"""
    ir_manager = IRManager()
    
    while True:
        console.clear()
        with console.status("[bold green]Loading devices...[/bold green]"):
            devices = ir_manager.get_devices()
        
        if not devices:
            console.print("[bold red]No devices found. Please run start_learning.py first.[/bold red]")
            return
        
        console.print(Panel.fit("[bold blue]IR Signal Sender[/bold blue]", 
                            subtitle="Press Ctrl+C to exit"))
        
        # Add navigation options
        console.print("\n[bold cyan]Navigation Options:[/bold cyan]")
        console.print("[b] Back to main menu")
        console.print("[x] Exit application")
        
        display_devices_and_signals(devices)
        
        # Select device or navigation option
        device_choice = Prompt.ask("\nSelect device number or navigation option", default="1")
        
        # Check for navigation commands
        if device_choice.lower() == 'b':
            return  # Exit to calling function
        elif device_choice.lower() == 'x':
            console.print("[bold green]👋 Goodbye![/bold green]")
            sys.exit(0)  # Exit application
        
        if not device_choice.isdigit():
            console.print("[bold red]Invalid device selection.[/bold red]")
            input("\nPress Enter to continue...")
            continue
        
        device_index = int(device_choice) - 1
        if device_index < 0 or device_index >= len(devices):
            console.print("[bold red]Invalid device number.[/bold red]")
            input("\nPress Enter to continue...")
            continue
        
        device = devices[device_index]
        console.print(f"[bold green]Selected device: [/bold green][yellow]{device['device_name']}[/yellow]")
        
        # Select signal
        signal_choice = Prompt.ask("\nSelect signal number (e.g., '1.2') or navigation option")
        
        # Check for navigation commands
        if signal_choice.lower() == 'b':
            continue  # Back to device selection
        elif signal_choice.lower() == 'x':
            console.print("[bold green]👋 Goodbye![/bold green]")
            sys.exit(0)  # Exit application
        
        parts = signal_choice.split('.')
        
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            d_idx = int(parts[0]) - 1
            s_idx = int(parts[1]) - 1
            
            if d_idx != device_index:
                console.print("[bold red]Device number in signal selection doesn't match selected device.[/bold red]")
                input("\nPress Enter to continue...")
                continue
                
            if s_idx < 0 or s_idx >= len(device["signals"]):
                console.print("[bold red]Invalid signal number.[/bold red]")
                input("\nPress Enter to continue...")
                continue
                
            signal = device["signals"][s_idx]
            console.print(f"[bold green]Selected signal: [/bold green][yellow]{signal['signal_name']}[/yellow]")
            
            # Send the signal
            with console.status("[bold green]Sending signal...[/bold green]"):
                success, message = ir_manager.send_signal(device["device_name"], signal["signal_name"])
            
            if success:
                console.print(f"[bold green]✅ {message}[/bold green]")
            else:
                console.print(f"[bold red]❌ {message}[/bold red]")
        else:
            console.print("[bold red]Invalid signal selection format. Use 'device.signal' format (e.g., '1.2').[/bold red]")
            input("\nPress Enter to continue...")

def list_devices():
    """Just list devices and signals"""
    ir_manager = IRManager()
    devices = ir_manager.get_devices()
    display_devices_and_signals(devices)

def send_specific_signal(device_name, signal_name):
    """Send a specific signal by name"""
    ir_manager = IRManager()
    
    with console.status("[bold green]Sending signal...[/bold green]"):
        success, message = ir_manager.send_signal(device_name, signal_name)
    
    if success:
        console.print(f"[bold green]✅ {message}[/bold green]")
    else:
        console.print(f"[bold red]❌ {message}[/bold red]")

def main():
    if len(sys.argv) == 1:
        # No arguments, enter interactive mode
        interactive_mode()
    elif len(sys.argv) == 2 and sys.argv[1] in ["-l", "--list"]:
        # Just list devices and signals
        list_devices()
    elif len(sys.argv) == 3:
        # Two arguments: device_name and signal_name
        device_name = sys.argv[1]
        signal_name = sys.argv[2]
        send_specific_signal(device_name, signal_name)
    else:
        console.print(Panel("""
[bold]Usage:[/bold]
  [green]python send_signal.py[/green]                   # Interactive mode
  [green]python send_signal.py -l[/green]                # List devices and signals
  [green]python send_signal.py device signal[/green]     # Send specific signal
        """, title="Help"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Program terminated by user.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")