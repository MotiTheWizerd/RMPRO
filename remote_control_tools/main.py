#!/usr/bin/env python3
from ir_manager import IRManager
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.layout import Layout
from rich import print as rprint
import sys
import os

console = Console()

def display_main_menu():
    """Display the main menu"""
    console.print(Panel.fit(
        "[bold blue]IR Remote Control Manager[/bold blue]",
        subtitle="Press Ctrl+C to exit"
    ))
    
    table = Table(show_header=False, box=None)
    table.add_column(style="cyan", justify="right")
    table.add_column(style="green")
    
    table.add_row("[1]", "Learn IR Signals")
    table.add_row("[2]", "Send IR Signals")
    table.add_row("[3]", "List All Devices and Signals")
    table.add_row("[4]", "Delete Device or Signal")
    table.add_row("[0]", "Exit")
    
    console.print(table)

def display_devices(devices, title="Available Devices"):
    """Display devices in a rich table"""
    if not devices:
        console.print(Panel("[yellow]No devices found[/yellow]", title=title))
        return
    
    table = Table(title=title)
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
    if not device:
        console.print(Panel("[yellow]No device selected[/yellow]", title="Signals"))
        return
    
    device_name = device.get("device_name", "Unknown Device")
    
    if "signals" not in device or not device["signals"]:
        console.print(Panel(f"[yellow]No signals found for device '{device_name}'[/yellow]", title="Signals"))
    
    table = Table(title=f"Signals for {device_name}")
    table.add_column("#", style="cyan", justify="right")
    table.add_column("Signal Name", style="green")
    table.add_column("Description", style="blue")
    
    # Add option for new signal
    table.add_row("[0]", "[bold]Create New Signal[/bold]", "")
    
    if device.get("signals"):
        for i, signal in enumerate(device["signals"], 1):
            table.add_row(
                f"[{i}]", 
                signal["signal_name"], 
                signal.get("signal_description", "")
            )
    
    console.print(table)

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
    # For new devices, device might be None
    if device is None:
        # This is a new device, so we need to create a new signal
        console.print("[yellow]This is a new device. Please create your first signal.[/yellow]")
        signal_name = Prompt.ask("Enter new signal name").strip().lower()
        if not signal_name:
            console.print("[bold red]Signal name cannot be empty.[/bold red]")
            return None, ""
        
        signal_description = Prompt.ask("Enter signal description (optional)", default="")
        return signal_name, signal_description
    
    # For existing devices
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
        elif "signals" in device and 1 <= index <= len(device["signals"]):
            signal = device["signals"][index - 1]
            return signal["signal_name"], signal.get("signal_description", "")
    
    console.print("[bold red]Invalid selection.[/bold red]")
    return None, ""

def learn_signals():
    """Learn IR signals"""
    ir_manager = IRManager()
    
    while True:
        console.clear()
        with console.status("[bold green]Loading devices...[/bold green]"):
            devices = ir_manager.get_devices()
        
        console.print(Panel.fit("[bold blue]IR Signal Learning Tool[/bold blue]", 
                            subtitle="Press Ctrl+C to exit"))
        
        # Add navigation options
        console.print("\n[bold cyan]Navigation Options:[/bold cyan]")
        console.print("[b] Back to main menu")
        console.print("[x] Exit application")
        
        # Display available devices
        display_devices(devices, title="Available Devices")
        
        # Select or create device
        device_choice = Prompt.ask("\nSelect device by number or navigation option", default="0")
        
        # Check for navigation commands
        if device_choice.lower() == 'b':
            return  # Back to main menu
        elif device_choice.lower() == 'x':
            console.print("[bold green]👋 Goodbye![/bold green]")
            sys.exit(0)  # Exit application
        
        # Handle device selection
        if device_choice.isdigit():
            index = int(device_choice)
            if index == 0:
                # Create new device
                device_name = Prompt.ask("Enter new device name").strip().lower()
                if not device_name:
                    console.print("[bold red]Device name cannot be empty.[/bold red]")
                    input("\nPress Enter to continue...")
                    continue
                
                device_description = Prompt.ask("Enter device description (optional)", default="")
            elif 1 <= index <= len(devices):
                device = devices[index - 1]
                device_name = device["device_name"]
                device_description = device.get("device_description", "")
            else:
                console.print("[bold red]Invalid selection.[/bold red]")
                input("\nPress Enter to continue...")
                continue
        else:
            console.print("[bold red]Invalid selection.[/bold red]")
            input("\nPress Enter to continue...")
            continue
        
        device = ir_manager.get_device(device_name)
        is_new_device = device is None
        
        if is_new_device:
            console.print(f"[bold green]Creating new device: [/bold green][yellow]{device_name}[/yellow]")
            # Create and save the device immediately
            success, message = ir_manager.create_device(device_name, device_description)
            if success:
                console.print(f"[bold green]✅ {message}[/bold green]")
                # Get the newly created device
                device = ir_manager.get_device(device_name)
            else:
                console.print(f"[bold red]❌ {message}[/bold red]")
        else:
            console.print(f"[bold green]Selected device: [/bold green][yellow]{device_name}[/yellow]")
        
        # Main loop for learning signals
        while True:
            try:
                console.print("\n[bold cyan]Navigation Options:[/bold cyan]")
                console.print("[b] Back to device selection")
                console.print("[m] Back to main menu")
                console.print("[x] Exit application")
                
                # Get updated device info
                device = ir_manager.get_device(device_name)
                
                # Display signals if device exists
                if device:
                    display_signals(device)
                
                # Select or create signal
                signal_choice = Prompt.ask("\nSelect signal by number or navigation option", default="0")
                
                # Check for navigation commands
                if signal_choice.lower() == 'b':
                    break  # Back to device selection
                elif signal_choice.lower() == 'm':
                    return  # Back to main menu
                elif signal_choice.lower() == 'x':
                    console.print("[bold green]👋 Goodbye![/bold green]")
                    sys.exit(0)  # Exit application
                
                # Handle signal selection
                if signal_choice.isdigit():
                    index = int(signal_choice)
                    if index == 0:
                        # Create new signal
                        signal_name = Prompt.ask("Enter new signal name").strip().lower()
                        if not signal_name:
                            console.print("[bold red]Signal name cannot be empty.[/bold red]")
                            continue
                        
                        signal_description = Prompt.ask("Enter signal description (optional)", default="")
                    elif device and "signals" in device and 1 <= index <= len(device["signals"]):
                        signal = device["signals"][index - 1]
                        signal_name = signal["signal_name"]
                        signal_description = signal.get("signal_description", "")
                    else:
                        console.print("[bold red]Invalid signal selection.[/bold red]")
                        continue
                else:
                    console.print("[bold red]Invalid selection.[/bold red]")
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
                choices = ["y", "n", "b", "m", "x"]
                action = Prompt.ask(
                    "\nLearn another signal? (y/n) or navigate (b=back, m=main menu, x=exit)", 
                    choices=choices, 
                    default="y"
                )
                
                if action == "n":
                    break
                elif action == "b":
                    break
                elif action == "m":
                    return
                elif action == "x":
                    console.print("[bold green]👋 Goodbye![/bold green]")
                    sys.exit(0)
                    
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Learning session interrupted.[/bold yellow]")
                if Prompt.ask("Return to main menu?", choices=["y", "n"], default="y") == "y":
                    return
                else:
                    break

def send_signals():
    """Send IR signals"""
    ir_manager = IRManager()
    
    while True:
        console.clear()
        with console.status("[bold green]Loading devices...[/bold green]"):
            devices = ir_manager.get_devices()
        
        if not devices:
            console.print("[bold red]No devices found. Please learn signals first.[/bold red]")
            input("\nPress Enter to return to main menu...")
            return
        
        console.print(Panel.fit("[bold blue]IR Signal Sender[/bold blue]", 
                            subtitle="Press Ctrl+C to exit"))
        
        # Add navigation options
        console.print("\n[bold cyan]Navigation Options:[/bold cyan]")
        console.print("[b] Back to main menu")
        console.print("[x] Exit application")
        
        try:
            # Create a flat list of all signals across all devices
            all_signals = []
            for device in devices:
                if device.get("signals"):
                    for signal in device["signals"]:
                        all_signals.append((device["device_name"], signal["signal_name"], signal.get("signal_description", "")))
            
            if not all_signals:
                console.print("[bold yellow]No signals found. Please learn signals first.[/bold yellow]")
                input("\nPress Enter to return to main menu...")
                return
            
            # Display all signals with simple numbering
            table = Table(title="Available Signals")
            table.add_column("#", style="cyan", justify="right")
            table.add_column("Device", style="green")
            table.add_column("Signal", style="magenta")
            table.add_column("Description", style="blue")
            
            for i, (device_name, signal_name, signal_desc) in enumerate(all_signals, 1):
                table.add_row(
                    f"[{i}]", 
                    device_name,
                    signal_name,
                    signal_desc
                )
            
            console.print(table)
            
            # Select signal by simple number or navigation option
            signal_choice = Prompt.ask("\nSelect signal number or navigation option", default="1")
            
            # Check for navigation commands
            if signal_choice.lower() == 'b':
                return  # Back to main menu
            elif signal_choice.lower() == 'x':
                console.print("[bold green]👋 Goodbye![/bold green]")
                sys.exit(0)  # Exit application
            
            # Handle signal selection
            if signal_choice.isdigit():
                signal_index = int(signal_choice) - 1
                if signal_index < 0 or signal_index >= len(all_signals):
                    console.print("[bold red]Invalid signal number.[/bold red]")
                    input("\nPress Enter to continue...")
                    continue
                
                # Get the selected signal
                device_name, signal_name, _ = all_signals[signal_index]
                console.print(f"[bold green]Selected signal: [/bold green][yellow]{device_name}.{signal_name}[/yellow]")
                
                # Send the signal
                with console.status("[bold green]Sending signal...[/bold green]"):
                    success, message = ir_manager.send_signal(device_name, signal_name)
                
                if success:
                    console.print(f"[bold green]✅ {message}[/bold green]")
                else:
                    console.print(f"[bold red]❌ {message}[/bold red]")
            else:
                console.print("[bold red]Invalid selection. Please enter a number or navigation option.[/bold red]")
                input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Sending session interrupted.[/bold yellow]")
            if Prompt.ask("Return to main menu?", choices=["y", "n"], default="y") == "y":
                return
            else:
                break
    
    console.print("[bold green]👋 Sending session completed.[/bold green]")

def list_all():
    """List all devices and signals with option to execute"""
    ir_manager = IRManager()
    
    while True:
        console.clear()
        with console.status("[bold green]Loading devices...[/bold green]"):
            devices = ir_manager.get_devices()
        
        console.print(Panel.fit("[bold blue]IR Devices and Signals[/bold blue]"))
        
        # Add navigation options
        console.print("\n[bold cyan]Navigation Options:[/bold cyan]")
        console.print("[b] Back to main menu")
        console.print("[x] Exit application")
        
        # Create a flat list of all signals across all devices
        all_signals = []
        for device in devices:
            if device.get("signals"):
                for signal in device["signals"]:
                    all_signals.append((device["device_name"], signal["signal_name"], signal.get("signal_description", "")))
        
        if not all_signals:
            console.print("[bold yellow]No signals found. Please learn signals first.[/bold yellow]")
            input("\nPress Enter to return to main menu...")
            return
        
        # Display all signals with simple numbering
        table = Table(title="Available Signals")
        table.add_column("#", style="cyan", justify="right")
        table.add_column("Device", style="green")
        table.add_column("Signal", style="magenta")
        table.add_column("Description", style="blue")
        
        for i, (device_name, signal_name, signal_desc) in enumerate(all_signals, 1):
            table.add_row(
                f"[{i}]", 
                device_name,
                signal_name,
                signal_desc
            )
        
        console.print(table)
        
        console.print("\n[italic]Enter a signal number to execute it, navigation option, or press Enter to return to menu[/italic]")
        choice = input().strip()
        
        if not choice:
            # User pressed Enter, return to main menu
            return
            
        # Check for navigation commands
        if choice.lower() == 'b':
            return  # Back to main menu
        elif choice.lower() == 'x':
            console.print("[bold green]👋 Goodbye![/bold green]")
            sys.exit(0)  # Exit application
        
        if choice.isdigit():
            signal_index = int(choice) - 1
            if 0 <= signal_index < len(all_signals):
                device_name, signal_name, _ = all_signals[signal_index]
                
                console.print(f"[bold]Executing signal: [/bold][yellow]{device_name}.{signal_name}[/yellow]")
                
                with console.status("[bold green]Sending signal...[/bold green]"):
                    success, message = ir_manager.send_signal(device_name, signal_name)
                
                if success:
                    console.print(f"[bold green]✅ {message}[/bold green]")
                else:
                    console.print(f"[bold red]❌ {message}[/bold red]")
                

            else:
                console.print(f"[bold red]Signal #{choice} not found. Please enter a valid signal number.[/bold red]")
        else:
            console.print("[bold red]Invalid input. Please enter a number or navigation option.[/bold red]")
        
        input("\nPress Enter to continue...")

def delete_item():
    """Delete a device or signal"""
    ir_manager = IRManager()
    
    console.clear()
    with console.status("[bold green]Loading devices...[/bold green]"):
        devices = ir_manager.get_devices()
    
    if not devices:
        console.print("[bold red]No devices found. Nothing to delete.[/bold red]")
        input("\nPress Enter to return to main menu...")
        return
    
    console.print(Panel.fit("[bold blue]Delete Device or Signal[/bold blue]"))
    
    # Add navigation options
    console.print("\n[bold cyan]Navigation Options:[/bold cyan]")
    console.print("[b] Back to main menu")
    console.print("[x] Exit application")
    
    # Ask what to delete
    console.print("\n[1] Delete a device")
    console.print("[2] Delete a signal")
    
    choice = Prompt.ask("\nWhat would you like to delete?", choices=["1", "2", "b", "x"], default="1")
    
    # Check for navigation commands
    if choice.lower() == 'b':
        return  # Back to main menu
    elif choice.lower() == 'x':
        console.print("[bold green]👋 Goodbye![/bold green]")
        sys.exit(0)  # Exit application
    
    if choice == "1":
        # Delete a device
        display_devices(devices, title="Select Device to Delete")
        
        # Add navigation options
        console.print("\n[bold cyan]Navigation Options:[/bold cyan]")
        console.print("[b] Back to main menu")
        console.print("[x] Exit application")
        
        device_choice = Prompt.ask("\nSelect device number to delete or navigation option")
        
        # Check for navigation commands
        if device_choice.lower() == 'b':
            return  # Back to main menu
        elif device_choice.lower() == 'x':
            console.print("[bold green]👋 Goodbye![/bold green]")
            sys.exit(0)  # Exit application
        
        if not device_choice.isdigit():
            console.print("[bold red]Invalid device selection.[/bold red]")
            input("\nPress Enter to continue...")
            return
        
        device_index = int(device_choice) - 1
        if device_index < 0 or device_index >= len(devices):
            console.print("[bold red]Invalid device number.[/bold red]")
            input("\nPress Enter to continue...")
            return
        
        device = devices[device_index]
        device_name = device["device_name"]
        
        # Confirm deletion
        confirm = Prompt.ask(
            f"Are you sure you want to delete device '{device_name}' and all its signals?", 
            choices=["y", "n", "b"], 
            default="n"
        )
        
        if confirm == "y":
            # Remove the device
            devices.pop(device_index)
            
            # Save the updated devices
            ir_manager.save_devices(devices)
            console.print(f"[bold green]✅ Device '{device_name}' deleted successfully.[/bold green]")
        elif confirm == "b":
            return  # Back to main menu
        else:
            console.print("[yellow]Deletion cancelled.[/yellow]")
    
    elif choice == "2":
        # Delete a signal
        display_devices(devices, title="Select Device")
        
        # Add navigation options
        console.print("\n[bold cyan]Navigation Options:[/bold cyan]")
        console.print("[b] Back to main menu")
        console.print("[x] Exit application")
        
        device_choice = Prompt.ask("\nSelect device number or navigation option")
        
        # Check for navigation commands
        if device_choice.lower() == 'b':
            return  # Back to main menu
        elif device_choice.lower() == 'x':
            console.print("[bold green]👋 Goodbye![/bold green]")
            sys.exit(0)  # Exit application
        
        if not device_choice.isdigit():
            console.print("[bold red]Invalid device selection.[/bold red]")
            input("\nPress Enter to continue...")
            return
        
        device_index = int(device_choice) - 1
        if device_index < 0 or device_index >= len(devices):
            console.print("[bold red]Invalid device number.[/bold red]")
            input("\nPress Enter to continue...")
            return
        
        device = devices[device_index]
        device_name = device["device_name"]
        
        if not device.get("signals"):
            console.print(f"[bold yellow]Device '{device_name}' has no signals to delete.[/bold yellow]")
            input("\nPress Enter to continue...")
            return
        
        # Display signals
        display_signals(device)
        
        # Add navigation options
        console.print("\n[bold cyan]Navigation Options:[/bold cyan]")
        console.print("[b] Back to main menu")
        console.print("[x] Exit application")
        
        signal_choice = Prompt.ask("\nSelect signal number to delete or navigation option")
        
        # Check for navigation commands
        if signal_choice.lower() == 'b':
            return  # Back to main menu
        elif signal_choice.lower() == 'x':
            console.print("[bold green]👋 Goodbye![/bold green]")
            sys.exit(0)  # Exit application
        
        if not signal_choice.isdigit():
            console.print("[bold red]Invalid signal selection.[/bold red]")
            input("\nPress Enter to continue...")
            return
        
        signal_index = int(signal_choice) - 1
        if signal_index < 0 or signal_index >= len(device["signals"]):
            console.print("[bold red]Invalid signal number.[/bold red]")
            input("\nPress Enter to continue...")
            return
        
        signal = device["signals"][signal_index]
        signal_name = signal["signal_name"]
        
        # Confirm deletion
        confirm = Prompt.ask(
            f"Are you sure you want to delete signal '{device_name}.{signal_name}'?", 
            choices=["y", "n", "b"], 
            default="n"
        )
        
        if confirm == "y":
            # Remove the signal
            device["signals"].pop(signal_index)
            
            # Save the updated devices
            ir_manager.save_devices(devices)
            console.print(f"[bold green]✅ Signal '{device_name}.{signal_name}' deleted successfully.[/bold green]")
        elif confirm == "b":
            return  # Back to main menu
        else:
            console.print("[yellow]Deletion cancelled.[/yellow]")
    
    input("\nPress Enter to return to main menu...")

def main():
    """Main function"""
    # Create signals directory if it doesn't exist
    os.makedirs("signals", exist_ok=True)
    
    # Initialize IR Manager and authenticate with Broadlink device
    console.print(Panel.fit("[bold blue]IR Remote Control Manager[/bold blue]", subtitle="Initializing..."))
    
    with console.status("[bold blue]Authenticating with Broadlink device...[/bold blue]"):
        ir_manager = IRManager()
        success, message = ir_manager.discover_and_auth()
    
    if success:
        console.print(Panel(f"[bold green]✅ {message}[/bold green]", title="Authentication Status"))
    else:
        console.print(Panel(f"[bold red]❌ {message}[/bold red]", title="Authentication Status"))
        console.print("[yellow]You can still use the app, but you may need to reconnect when sending signals.[/yellow]")
    
    input("\nPress Enter to continue to main menu...")
    
    while True:
        try:
            console.clear()
            display_main_menu()
            
            choice = Prompt.ask("\nSelect an option", choices=["0", "1", "2", "3", "4"], default="1")
            
            if choice == "0":
                console.print("[bold green]👋 Goodbye![/bold green]")
                break
            elif choice == "1":
                learn_signals()
            elif choice == "2":
                send_signals()
            elif choice == "3":
                list_all()
            elif choice == "4":
                delete_item()
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Program interrupted by user.[/bold yellow]")
            break
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"[bold red]Unhandled error: {e}[/bold red]")
        sys.exit(1)