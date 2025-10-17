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

Run the provided setup script:

```bash
./bin/setup_usb_permissions.sh
```

This script will:
- Create the necessary udev rules
- Add your user to the `plugdev` group (if the group exists)
- Reload the udev rules automatically

**Important:** After running the script, you need to either:
- Log out and log back in, OR
- Reboot your system

Then unplug and replug your LED device for the new permissions to take effect.

### Verify USB device is detected

```bash
lsusb | grep 0416:5020
```

You should see your LED device listed.

## Installation as CLI Tool

After syncing dependencies, the `led-fun` command will be available via `uv run`:

```bash
uv sync
```

Then use the command:

```bash
uv run led-fun "Hello World"
```

## Usage

### Basic Usage

Display a message on your LED badge:

```bash
uv run led-fun "Hello World"
```

### Multiple Messages

Display up to 8 different messages:

```bash
uv run led-fun "Message 1" "Message 2" "Message 3"
```

### With Options

Customize speed, brightness, mode, etc.:

```bash
uv run led-fun "Hello" --speed 5 --brightness 75 --mode 0
```

### Using Icons

Embed built-in icons in your messages using colon notation:

```bash
uv run led-fun "I:ball:you"
```

### List Available Icons

See all available built-in icons:

```bash
uv run led-fun --list-icons
```

### Available Options

- `--speed, -s`: Scroll speed (Range 1..8). Up to 8 comma-separated values. Default: 4
- `--brightness, -B`: Brightness percentage (25, 50, 75, or 100). Default: 100
- `--mode, -m`: Display mode:
  - 0: Scroll-left
  - 1: Scroll-right
  - 2: Scroll-up
  - 3: Scroll-down
  - 4: Still-centered
  - 5: Animation
  - 6: Drop-down
  - 7: Curtain
  - 8: Laser
- `--blink, -b`: Blinking (1) or normal (0). Default: 0
- `--ants, -a`: Animated border (1) or normal (0). Default: 0
- `--preload, -p`: Load bitmap images (deprecated, use `:path:` notation instead)

### Examples

```bash
# Simple message with custom speed
uv run led-fun "Hello World" --speed 6

# Multiple messages with different modes
uv run led-fun "Scroll Left" "Still Text" --mode "0,4" --speed "5,1"

# Message with icon and custom brightness
uv run led-fun ":ball: Hello :ball:" --brightness 50

# Blinking message with animated border
uv run led-fun "URGENT" --blink 1 --ants 1 --brightness 100
```

### Detect Available LED Devices

To detect available LED devices without sending a message:

```bash
uv run python -m led_fun.main
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

## Help

To see all available options and their descriptions:

```bash
uv run led-fun --help
```

## Development

This project uses:
- **uv** for dependency management and packaging
- **pyproject.toml** for project configuration
- **typer** for CLI interface
- Python 3.13+ features

### Adding Dependencies

To add new dependencies:

```bash
uv add <package-name>
```

### CLI Entry Point

The project includes a CLI entry point configured in `pyproject.toml`:

```toml
[project.scripts]
led-fun = "led_fun.usb_badge:cli_entry"
```

This allows the `led-fun` command to be available after installation.

## License

See [LICENSE](LICENSE) file for details.
