from ir_manager import IRManager
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import print as rprint
import time

console = Console()

def display_devices(devices):
    """Display devices in a rich table"""
    if not devices:
        console.print(Panel("[yellow]No devices found[/yellow]", title="Devices"))
        return
    
    table = Table(title="Available Devices")
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Device Name", style="green")
    table.add_column("Description", style="blue")
    table.add_column("Signals", style="magenta")
    
    # Add option for new device
    table.add_row("[0]", "[bold]Create New Device[/bold]", "", "")
    
    for i, device in enumerate(devices, 1):
        signal_count = len(device.get("signals", []))
        table.add_row(
            f"[{i}]", 
            device["device_name"], 
            device.get("device_description", ""), 
            f"{signal_count} signal(s)"
        )
    
    console.print(table)

def display_signals(device):
    """Display signals for a device in a rich table"""
    if not device or "signals" not in device or not device["signals"]:
        console.print(Panel(f"[yellow]No signals found for device '{device['device_name']}'[/yellow]", title="Signals"))
        return
    
    table = Table(title=f"Signals for {device['device_name']}")
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Signal Name", style="green")
    table.add_column("Description", style="blue")
    
    # Add option for new signal
    table.add_row("[0]", "[bold]Create New Signal[/bold]", "")
    
    for i, signal in enumerate(device["signals"], 1):
        table.add_row(
            f"[{i}]", 
            signal["signal_name"], 
            signal.get("signal_description", "")
        )
    
    console.print(table)

def select_device(devices):
    """Let user select a device by number or create a new one"""
    if not devices:
        return None, ""
    
    display_devices(devices)
    
    choice = Prompt.ask("\nSelect device by number", default="0")
    
    # Check if choice is a number
    if choice.isdigit():
        index = int(choice)
        if index == 0:
            # Create new device
            device_name = Prompt.ask("Enter new device name").strip().lower()
            if not device_name:
                console.print("[bold red]Device name cannot be empty.[/bold red]")
                return None, ""
            
            device_description = Prompt.ask("Enter device description (optional)", default="")
            return device_name, device_description
        elif 1 <= index <= len(devices):
            device = devices[index - 1]
            return device["device_name"], device.get("device_description", "")
    
    console.print("[bold red]Invalid selection.[/bold red]")
    return None, ""

def select_signal(device):
    """Let user select a signal by number or create a new one"""
    display_signals(device)
    
    choice = Prompt.ask("\nSelect signal by number", default="0")
    
    # Check if choice is a number
    if choice.isdigit():
        index = int(choice)
        if index == 0:
            # Create new signal
            signal_name = Prompt.ask("Enter new signal name").strip().lower()
            if not signal_name:
                console.print("[bold red]Signal name cannot be empty.[/bold red]")
                return None, ""
            
            signal_description = Prompt.ask("Enter signal description (optional)", default="")
            return signal_name, signal_description
        elif device and "signals" in device and 1 <= index <= len(device["signals"]):
            signal = device["signals"][index - 1]
            return signal["signal_name"], signal.get("signal_description", "")
    
    console.print("[bold red]Invalid selection.[/bold red]")
    return None, ""

def main():
    ir_manager = IRManager()
    
    with console.status("[bold green]Loading devices...[/bold green]"):
        devices = ir_manager.get_devices()
    
    console.print(Panel.fit("[bold blue]IR Signal Learning Tool[/bold blue]", 
                           subtitle="Press Ctrl+C to exit"))
    
    # Select or create device
    device_name, device_description = select_device(devices)
    if not device_name:
        return
    
    device = ir_manager.get_device(device_name)
    is_new_device = device is None
    
    if is_new_device:
        console.print(f"[bold green]Creating new device: [/bold green][yellow]{device_name}[/yellow]")
    else:
        console.print(f"[bold green]Selected device: [/bold green][yellow]{device_name}[/yellow]")
    
    # Main loop for learning signals
    while True:
        try:
            # Get updated device info
            device = ir_manager.get_device(device_name)
            
            # Select or create signal
            signal_name, signal_description = select_signal(device)
            if not signal_name:
                continue
            
            # Learn the signal
            console.print(f"\n[bold]Learning signal: [/bold][yellow]{device_name}.{signal_name}[/yellow]")
            console.print("[bold cyan]🕹️ Press the button on your remote...[/bold cyan]")
            
            with console.status("[bold green]Waiting for signal...[/bold green]"):
                success, message = ir_manager.learn_signal(
                    device_name, signal_name, signal_description, device_description
                )
            
            if success:
                console.print(f"[bold green]✅ {message}[/bold green]")
            else:
                console.print(f"[bold red]❌ {message}[/bold red]")
            
            # Ask if user wants to continue
            if not Confirm.ask("\nLearn another signal?"):
                break
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Learning session interrupted.[/bold yellow]")
            break
    
    console.print("[bold green]👋 Learning session completed.[/bold green]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Program terminated by user.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")