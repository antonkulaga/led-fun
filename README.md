# led-fun

Experiments with LED programming using USB-controlled LED devices.

## Prerequisites

- Python 3.13 or higher
- [uv](https://github.com/astral-sh/uv) - Python package manager
- USB LED device (Vendor ID: 0x0416, Product ID: 0x5020)

## Installation

### 1. Install uv

If you don't have `uv` installed yet:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the repository

```bash
git clone https://github.com/antonkulaga/led-fun.git
cd led-fun
```

### 3. Install dependencies

Using `uv`, the dependencies will be automatically installed when you run the project:

```bash
uv sync
```

## USB Permissions Setup (Linux)

On Linux, you need to set up proper USB device permissions to access the LED device without root privileges.

### Create a udev rule

1. Create a new udev rules file:

```bash
sudo nano /etc/udev/rules.d/99-led-device.rules
```

2. Add the following rule (replace `YOUR_USERNAME` with your actual username):

```
SUBSYSTEM=="usb", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="5020", MODE="0666", GROUP="plugdev"
```

Or to allow access for a specific user:

```
SUBSYSTEM=="usb", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="5020", MODE="0666", OWNER="YOUR_USERNAME"
```

3. Reload udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

4. Unplug and replug your LED device.

### Verify USB device is detected

```bash
lsusb | grep 0416:5020
```

You should see your LED device listed.

## Usage

Run the main script to detect available LED devices:

```bash
uv run python -m led_fun.main
```

Or activate the virtual environment first:

```bash
source .venv/bin/activate
python -m led_fun.main
```

## Troubleshooting

### "No device found" error

- Make sure the USB device is properly connected
- Check if the device is detected: `lsusb | grep 0416:5020`
- Verify udev rules are properly configured
- Try running with sudo (not recommended for regular use): `sudo uv run python -m led_fun.main`

### Permission denied errors

- Ensure you've set up the udev rules correctly
- Make sure your user is in the `plugdev` group: `sudo usermod -a -G plugdev $USER`
- Log out and log back in for group changes to take effect
- Alternatively, reboot your system

### PyUSB backend errors

If you get an error about no backend available, you may need to install libusb:

```bash
# Ubuntu/Debian
sudo apt-get install libusb-1.0-0

# Fedora
sudo dnf install libusb

# Arch
sudo pacman -S libusb
```

## Development

This project uses:
- **uv** for dependency management
- **pyproject.toml** for project configuration
- Python 3.13+ features

To add new dependencies:

```bash
uv add <package-name>
```

## License

See [LICENSE](LICENSE) file for details.
