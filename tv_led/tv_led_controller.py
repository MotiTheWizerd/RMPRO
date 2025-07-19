from bleak import BleakClient
import asyncio

ADDRESS = "35:04:14:20:01:29"  # Replace with your device if needed

async def main():
    async with BleakClient(ADDRESS) as client:
        services = await client.get_services()
        for service in services:
            print(f"Service: {service.uuid}")
            for char in service.characteristics:
                print(f"  └── Characteristic: {char.uuid} | Properties: {char.properties}")

asyncio.run(main())
