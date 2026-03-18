import asyncio
from bleak import BleakClient
from pynput.keyboard import Key, Controller
import kickr.scanner
import kickr.uuids
import kickr.buttons as buttons

# --- CONFIGURATION ---
# Choose your KICKR button from buttons.Button_bits (e.g., Steer_Left, Shift_Back_Right)
TARGET_KICKR_BUTTON = buttons.Button_bits.Top_Front_Right 

# Choose your Keyboard Key (e.g., 'v', Key.f10, Key.ctrl_l)
TARGET_KEY = 'v' 
# ---------------------

keyboard = Controller()

def unsigned_16(low, high):
    return (high << 8) | low

def ptt_handler(characteristic, data: bytearray):
    """Custom handler to detect holds and trigger keystrokes"""
    # We only care about the 3-byte 'event' packets for precise timing
    if len(data) == 3:
        bitfield = unsigned_16(data[0], data[1])
        is_down = (data[2] & 0x80) == 0x80
        
        # Check if the button pressed matches our target
        if bitfield == TARGET_KICKR_BUTTON.value:
            if is_down:
                print(f"PTT ACTIVE: Holding [{TARGET_KEY}]")
                keyboard.press(TARGET_KEY)
            else:
                print(f"PTT INACTIVE: Releasing [{TARGET_KEY}]")
                keyboard.release(TARGET_KEY)

async def main():
    kickr.uuids.register_uuids()

    print("Searching for KICKR...")
    device = await kickr.scanner.find_kickr()
    if not device:
        print("KICKR not found.")
        return

    print(f"Connecting to {device.name}...")
    async with BleakClient(device) as client:
        # We manually use our ptt_handler instead of the one in buttons.py
        # Ensure kickr_buttons UUID was fixed in your uuids.py earlier!
        await client.start_notify(kickr.uuids.kickr_buttons, ptt_handler)
        
        print(f"SUCCESS: {TARGET_KICKR_BUTTON.name} is now mapped to '{TARGET_KEY}'")
        print("Press Ctrl+C to stop and disconnect.")

        try:
            while client.is_connected:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        finally:
            # Safety: Always release the key on exit so it doesn't get 'stuck' down
            keyboard.release(TARGET_KEY)
            print("\nKey released. Disconnecting...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
