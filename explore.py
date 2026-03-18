import asyncio
from bleak import BleakClient

# Replace with the address you found using kickr_scan.py
ADDRESS = "7D575778-5291-0FF4-5AA8-89B2232D451D" 

async def main(address):
    client = BleakClient(address, timeout=20.0)
    try:
        print(f"Attempting to connect to {address}...")
        await client.connect()
        print(f"Connected: {client.is_connected}")

        # In modern Bleak, services are accessed via the .services property
        for service in client.services:
            print(f"\nService: {service.uuid} ({service.description})")
            for char in service.characteristics:
                print(f"  Characteristic: {char.uuid}")
                print(f"    Properties: {', '.join(char.properties)}")
                
    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main(ADDRESS))

