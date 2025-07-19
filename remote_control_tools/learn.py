from ir_manager import IRManager

def learn_and_save(device_name: str, signal_name: str, signal_description: str = "", device_description: str = "", folder="signals"):
    """Learn and save an IR signal using the IRManager class"""
    # Create an instance of IRManager
    ir_manager = IRManager(folder=folder)
    
    print(f"🕹️ Press the button for '{device_name}.{signal_name}'...")
    
    # Use the IRManager to learn the signal
    success, message = ir_manager.learn_signal(
        device_name, 
        signal_name, 
        signal_description, 
        device_description
    )
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    
    return success

# Example usage (commented out)
# learn_and_save("ac", "off")