#!/usr/bin/env python3
import sys
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add the project root to the path so we can import all necessary modules
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
# Also add the project root to PYTHONPATH environment variable
os.environ["PYTHONPATH"] = project_root
from agents.device_control_agent.utils.execute_ir_command_tool import execute_ir_command

console = Console()

def display_result(result, command):
    """Display the result of an IR command execution in a nice format"""
    if result["success"]:
        console.print(Panel(
            f"[bold green]✅ Command executed successfully[/bold green]\n\n{result['message']}",
            title=f"Command: {command}"
        ))
        if "signal" in result:
            signal = result["signal"]
            console.print("\n[bold]Signal Details:[/bold]")
            console.print(f"  Device: [green]{signal['device_name']}[/green]")
            console.print(f"  Signal: [magenta]{signal['signal_name']}[/magenta]")
            console.print(f"  Description: [blue]{signal['signal_description']}[/blue]")
            console.print(f"  ID: [yellow]{signal['signal_id']}[/yellow]")
    else:
        console.print(Panel(
            f"[bold red]❌ Command failed[/bold red]\n\n{result['message']}",
            title=f"Command: {command}"
        ))
        
        if "matches" in result and result["matches"]:
            console.print("\n[bold]Found these matching signals:[/bold]")
            
            table = Table()
            table.add_column("#", style="cyan", justify="right")
            table.add_column("Device", style="green")
            table.add_column("Signal", style="magenta")
            table.add_column("Description", style="blue")
            table.add_column("ID", style="yellow")
            
            for i, signal in enumerate(result["matches"], 1):
                table.add_row(
                    f"[{i}]",
                    signal["device_name"],
                    signal["signal_name"],
                    signal["signal_description"],
                    signal["signal_id"]
                )
            
            console.print(table)
            
            # If there are matches, offer to execute one of them
            if len(result["matches"]) > 0:
                console.print("\n[bold]Would you like to execute one of these signals?[/bold]")
                try:
                    choice = input("Enter the number or press Enter to skip: ")
                    if choice.isdigit() and 1 <= int(choice) <= len(result["matches"]):
                        signal = result["matches"][int(choice) - 1]
                        console.print(f"\nExecuting signal: [bold]{signal['device_name']}.{signal['signal_name']}[/bold]")
                        execute_result = execute_ir_command(signal["signal_id"])
                        display_result(execute_result, signal["signal_id"])
                except KeyboardInterrupt:
                    console.print("\n[yellow]Operation cancelled.[/yellow]")

def run_test():
    """Run tests for the execute_ir_command function"""
    console.print(Panel.fit("[bold blue]IR Command Test Tool[/bold blue]"))
    
    while True:
        console.print("\n[bold cyan]Options:[/bold cyan]")
        console.print("1. Execute command by ID")
        console.print("2. Execute command by search term")
        console.print("3. List all available signals")
        console.print("0. Exit")
        
        try:
            choice = input("\nEnter your choice: ")
            
            if choice == "0":
                console.print("[bold green]Goodbye![/bold green]")
                break
                
            elif choice == "1":
                signal_id = input("\nEnter signal ID: ")
                result = execute_ir_command(signal_id)
                display_result(result, signal_id)
                
            elif choice == "2":
                search_term = input("\nEnter search term: ")
                result = execute_ir_command(search_term)
                display_result(result, search_term)
                
            elif choice == "3":
                # Import the function to list all signals
                from remote_control_tools.send_by_id import display_signals
                display_signals()
                
            else:
                console.print("[bold red]Invalid choice. Please try again.[/bold red]")
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Operation cancelled.[/bold yellow]")
            if input("Exit? (y/n): ").lower() == 'y':
                console.print("[bold green]Goodbye![/bold green]")
                break
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")

if __name__ == "__main__":
    run_test()