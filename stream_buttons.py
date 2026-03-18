import asyncio
import yaml
import os
from bleak import BleakClient
from pynput.keyboard import Key, Controller
import kickr.scanner
import kickr.uuids
import kickr.buttons as buttons

CONFIG_FILE = "config.yaml"

def load_config():
    # Default structure with the new nested keys
    default = {
        "ptt": {
            "kickr_button": "Top_Front_Left_Decline",
            "keyboard_key": "v"
        }
    }
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(default, f, default_flow_style=False)
    
    with open(CONFIG_FILE, "r") as f:
        return yaml.safe_load(f)

# Load and Map Config
config = load_config()
keyboard = Controller()

try:
    # Access nested ptt settings
    ptt_cfg = config.get('ptt', {})
    btn_str = ptt_cfg.get('kickr_button', 'Steer_Left')
    key_str = ptt_cfg.get('keyboard_key', 'v').lower()

    TARGET_KICKR_BUTTON = getattr(buttons.Button_bits, btn_str)
    TARGET_KEY = getattr(Key, key_str) if hasattr(Key, key_str) else key_str
except Exception as e:
    print(f"Config Error: {e}. Check your spelling in config.yaml")
    exit(1)

def ptt_handler(characteristic, data: bytearray):
    if len(data) == 3:
        # Standard Wahoo 3-byte event: [bit_low, bit_high, state]
        bitfield = (data[1] << 8) | data[0]
        is_down = (data[2] & 0x80) == 0x80
        
        if bitfield == TARGET_KICKR_BUTTON.value:
            if is_down:
                print(f"PTT ON: [{TARGET_KEY}]")
                keyboard.press(TARGET_KEY)
            else:
                print(f"PTT OFF: [{TARGET_KEY}]")
                keyboard.release(TARGET_KEY)

async def main():
    kickr.uuids.register_uuids()
    print("Searching for KICKR...")
    device = await kickr.scanner.find_kickr()
    if not device: return

    async with BleakClient(device) as client:
        # Ensure uuids.py: kickr_buttons = normalize_wahoo_uuid(0xe03a)
        await client.start_notify(kickr.uuids.kickr_buttons, ptt_handler)
        print(f"Running: {btn_str} -> {key_str}")

        try:
            while client.is_connected:
                await asyncio.sleep(0.1)
        finally:
            keyboard.release(TARGET_KEY) # Safety release

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
