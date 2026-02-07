# Wiimote-to-Android USB Gamepad Bridge

Turn a **Raspberry Pi Zero W** into a wireless Wiimote-to-USB gamepad adapter.  
The Pi connects to up to **4 Wiimotes** via Bluetooth and presents them to an Android phone as standard **USB HID gamepads** over the OTG port — no app or driver needed on Android.

```
Wiimote(s) ──[Bluetooth]──▶ Pi Zero W ──[USB OTG]──▶ Android Phone
                              (bridge)              (sees USB gamepads)
```

## Features

- **Headless operation** — starts automatically on boot via systemd
- **Auto-scanning** — continuously looks for Wiimotes; reconnects on disconnect
- **4-player support** — each Wiimote gets its own player LED (1–4) and HID device
- **Sequential assignment** — first Wiimote always becomes P1, then P2, etc.
- **D-Pad as hat switch** — proper directional input recognized as D-Pad on Android
- **7 buttons** — A, B, 1, 2, Plus, Minus, Home all mapped as gamepad buttons
- **Accelerometer** — tilt is mapped to analog stick axes (X/Y)
- **Instant Android support** — Android natively recognizes USB HID gamepads
- **Recalibrate on the fly** — hold Home for 5s to recalibrate the accelerometer zero-point
- **Clean disconnect** — hold + and − together for 5s on the Wiimote

## Button Mapping

| Wiimote         | Gamepad Output       | HID Field         |
|-----------------|----------------------|--------------------|
| D-Pad           | Hat Switch (D-Pad)   | 4-bit hat (byte 2) |
| A               | Button A             | bit 0 (byte 3)    |
| B               | Button B             | bit 1 (byte 3)    |
| 1               | Button C             | bit 2 (byte 3)    |
| 2               | Button X             | bit 3 (byte 3)    |
| Plus            | Button Y             | bit 4 (byte 3)    |
| Minus           | Button Z             | bit 5 (byte 3)    |
| Home            | Button Mode          | bit 6 (byte 3)    |
| Tilt left/right | X Axis (analog)      | signed byte 0     |
| Tilt fwd/back   | Y Axis (analog)      | signed byte 1     |
| + and − (hold 5s) | Disconnect Wiimote | —                  |
| Home (hold 5s)  | Recalibrate accel    | —                  |

## Requirements

- Raspberry Pi Zero W (with Bluetooth)
- Raspberry Pi OS (Bookworm or Bullseye)
- Micro-USB **data** cable (not power-only)
- One to four Nintendo Wiimotes

## Installation

1. **Clone** this repo onto the Pi (or copy the files via SCP):

   ```bash
   git clone https://github.com/YOUR_USER/wii-mote.git
   cd wii-mote
   ```

2. **Run the installer** as root:

   ```bash
   sudo bash install.sh
   ```

   This will:
   - Install `python3-cwiid`, `bluetooth`, `bluez`, and other dependencies
   - Add `dtoverlay=dwc2` to boot config
   - Add `dwc2` and `libcomposite` kernel modules
   - Copy files to `/opt/wiimote-bridge/`
   - Install and enable systemd services
   - Set up udev rules for `/dev/hidg*`

3. **Reboot** the Pi (the installer will prompt you).

## Usage

1. Connect the Pi Zero W to your Android phone using a micro-USB data cable into the **data port** (the one closer to the center of the board, NOT the power-only port on the edge).

2. The bridge service starts automatically. Check status:

   ```bash
   systemctl status wiimote-bridge.service
   ```

3. **Press 1 + 2** on a Wiimote. The Pi will connect it:
   - Player 1: LED 1 lights up (first Wiimote always gets P1)
   - Player 2: LED 2 lights up
   - Player 3: LED 3 lights up
   - Player 4: LED 4 lights up
   - A brief rumble confirms the connection

4. Open any game or gamepad tester app on Android — the Wiimote inputs will appear as a standard USB gamepad.

5. To **disconnect** a Wiimote: hold **+ and −** together for 5 seconds (brief rumble, then the slot starts scanning again).

6. To **recalibrate** the accelerometer: hold the Wiimote flat/still and hold **Home** for 5 seconds.

## Logs & Debugging

```bash
# Live logs
journalctl -u wiimote-bridge.service -f

# Check if HID gadget devices exist
ls -la /dev/hidg*

# Check gadget setup service
systemctl status wiimote-gadget.service

# Check Bluetooth
bluetoothctl show
```

## File Structure

```
wii-mote/
├── install.sh                          # One-step installer
├── wiimote_bridge.py                   # Main bridge daemon
├── scripts/
│   ├── setup_usb_gadget.sh            # Creates USB HID gadget (configfs)
│   └── teardown_usb_gadget.sh         # Removes USB HID gadget
├── systemd/
│   ├── wiimote-gadget.service         # Gadget setup on boot
│   └── wiimote-bridge.service         # Bridge daemon service
└── udev/
    └── 99-hidg.rules                  # /dev/hidg* permissions
```

## Uninstall

```bash
sudo systemctl stop wiimote-bridge.service
sudo systemctl stop wiimote-gadget.service
sudo systemctl disable wiimote-bridge.service
sudo systemctl disable wiimote-gadget.service
sudo rm /etc/systemd/system/wiimote-gadget.service
sudo rm /etc/systemd/system/wiimote-bridge.service
sudo rm /etc/udev/rules.d/99-hidg.rules
sudo rm -rf /opt/wiimote-bridge
sudo systemctl daemon-reload
```

Remove `dtoverlay=dwc2` from `/boot/firmware/config.txt` and `dwc2`/`libcomposite` from `/etc/modules` if no longer needed, then reboot.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `/dev/hidg0` doesn't exist | Check `systemctl status wiimote-gadget.service`. Ensure `dtoverlay=dwc2` is in boot config and you've rebooted. |
| Wiimote won't connect | Make sure Bluetooth is on (`bluetoothctl show`). Press 1+2 on Wiimote within a few seconds. Try moving closer to the Pi. |
| Android doesn't detect gamepad | Use the **data port** (inner micro-USB), not the power port. Use a data-capable cable. |
| High latency | Disable WiFi to free the shared BT/WiFi radio: `sudo rfkill block wifi` |
| Bridge keeps restarting | Check logs: `journalctl -u wiimote-bridge.service -e`. Usually a missing `python3-cwiid` package. |

## Credits

Built by **c4g7** ([@c4g7-dev](https://github.com/c4g7-dev)) and **Cedrik**.

## License

MIT
