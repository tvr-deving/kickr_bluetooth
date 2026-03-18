# kickr_bluetooth

## Introduction
This repository contains information on how to connect to the KICKR Bike via Bluetooth Smart / BLE.
As I discover more about the bike, I will add the information here.
I intend to write some sample scripts to help others get started with their projects.
I hope that the information here helps people get started with Bluetooth Low Energy and/or create some interesting projects with their exercise equipment.

## Documentation
See the [Wiki](../../wiki) for documentation. 

## Background
As a separate project that is not on GitHub, I have been writing an indoor cycling data logging app for my (KICKR) bike, my Heart Rate Monitor and my muscle oxygenation sensors (Train.Red).
Since my KICKR bike is the only Bluetooth enabled indoor trainer I have access to, I have been investigating what features it has, that I can make use of in my app.

## 🎙️ Push-to-Talk (PTT) Feature
This fork includes a standalone script, `stream_buttons.py`, which allows you to map any KICKR Bike button to a keyboard key for Push-to-Talk (Discord, TeamSpeak, etc.). The key remains "held" as long as you hold the physical button.

### How to Run
1. **Configure:** Edit `config.yaml` to set your desired button and key:
   ```yaml
   ptt:
     kickr_button: "Steer_Left"  # Options: Steer_Left, Steer_Right, Shift_Back_Left, etc.
     keyboard_key: "v"           # Any character or special key (e.g., "f10", "ctrl_l")
2. **Install Dependencies:** pip install -r requirements.txt
3. **Execute:** Run python stream_buttons.py. The script will automatically discover your KICKR and begin mapping.

## 🔍 Troubleshooting & Debugging UUIDs

If the script crashes with a `bleak.exc.BleakCharacteristicNotFoundError`, your KICKR firmware likely uses different UUIDs than the original repository defaults.

### 1. Identify your UUIDs
Run the discovery section in `kickr_gatt.py` (or a custom explorer script) to see available services. Look for a Service ending in `ee0d` and a Characteristic with the `notify` property.

### 2. Update `kickr/uuids.py`
If your KICKR is a newer model (V5/V6/BIKE V2), you often need to swap the values in `kickr/uuids.py`. A common fix is changing the button ID to `e03a`:
```python
# In kickr/uuids.py
kickr_buttons = normalize_wahoo_uuid(0xe03a)  # Change from 0xe03c if it fails
```
### 3. Connection Issues
* **Windows:** Ensure the KICKR is **NOT** paired in Windows Bluetooth settings before running. The script needs an unmanaged connection to hook into the custom Wahoo services.
* **Other Apps:** Ensure the Wahoo Fitness app, Zwift, or any other training software is completely closed. Most KICKRs have a limit on concurrent Bluetooth connections.
* **Linux:** Ensure your user has permissions for the Bluetooth stack or run the script with `sudo`.
* **Caching:** If you recently updated your KICKR firmware, Windows may cache old service definitions. "Forget" the device in your OS settings and power cycle the KICKR to force a fresh scan.

### 4. Device Discovery & Debugging
If you are still unable to connect or find the correct buttons, use the `explore.py` tool included in this repository. This script scans all available Bluetooth services and characteristics on your KICKR and prints them to the console.

**To run the explorer:**
1. Find your KICKR's Bluetooth address using `python kickr_scan.py`.
2. Update the `ADDRESS` variable in `explore.py`.
3. Run `python explore.py`.

Look for characteristics that support **Notify**. These are the data streams for buttons and power data. If you see different UUIDs than those in `kickr/uuids.py`, update them to match your hardware's specific firmware version.
