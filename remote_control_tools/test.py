from ir_manager import IRManager
from rich.console import Console
from rich.table import Table

console = Console()

def test_ir_manager():
    """Test the IRManager class functionality"""
    console.print("[bold blue]Testing IR Manager...[/bold blue]")
    
    # Initialize manager
    ir_manager = IRManager()
    
    # Get devices
    devices = ir_manager.get_devices()
    console.print(f"Found {len(devices)} device(s)")
    
    # Display devices in a table
    if devices:
        table = Table(title="Devices")
        table.add_column("Device Name")
        table.add_column("Description")
        table.add_column("Signal Count")
        
        for device in devices:
            table.add_row(
                device["device_name"],
                device.get("device_description", ""),
                str(len(device.get("signals", [])))
            )
        
        console.print(table)
        
        # Show signals for first device
        if devices and devices[0].get("signals"):
            device = devices[0]
            console.print(f"\n[bold]Signals for {device['device_name']}:[/bold]")
            
            signal_table = Table()
            signal_table.add_column("Signal Name")
            signal_table.add_column("Description")
            
            for signal in device["signals"]:
                signal_table.add_row(
                    signal["signal_name"],
                    signal.get("signal_description", "")
                )
            
            console.print(signal_table)
    
    console.print("[bold green]Test completed![/bold green]")

if __name__ == "__main__":
    test_ir_manager()