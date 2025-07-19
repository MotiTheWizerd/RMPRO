import os, platform

def ping_sweep(subnet="192.168.1", start=1, end=254):
    print("Scanning your LAN...")
    ping_cmd = "ping -n 1" if platform.system().lower() == "windows" else "ping -c 1"
    for i in range(start, end + 1):
        ip = f"{subnet}.{i}"
        response = os.system(f"{ping_cmd} {ip} > nul")
        if response == 0:
            print(f"✅ {ip} is alive")

ping_sweep()