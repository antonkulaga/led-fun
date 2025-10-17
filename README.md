# led-fun

A Python library and CLI tool for controlling LED badge displays via USB. Display custom text, animations, and icons on 11x44 LED badge devices.

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

## Architecture

The project is organized into modular components for maintainability and clarity:

### Module Structure

```
led_fun/
├── __init__.py       # Public API exports
├── font.py           # Font data and bitmap conversion
├── device.py         # USB communication layer
├── cli.py            # Command-line interface
└── main.py           # Device detection utility
```

### Modules

#### `font.py` - Font and Bitmap Handling
Contains the `SimpleTextAndIcons` class which handles:
- Character font data storage (11x44 pixel format)
- Text-to-bitmap conversion
- Icon embedding and image loading
- Support for special characters and international characters

#### `device.py` - USB Communication
Contains two main classes:
- `WriteLibUsb`: Low-level USB communication using pyusb
- `LedNameBadge`: High-level protocol handler for LED badges

Handles:
- USB device detection and initialization
- Protocol header generation
- Data transmission to LED displays

#### `cli.py` - Command-Line Interface
Provides the user-facing CLI using Typer:
- Message formatting and validation
- Parameter parsing (speed, mode, brightness, etc.)
- Coordination between font and device modules

### How Text is Converted to LEDs

The LED display uses a bitmap-based character encoding system:

#### Character Format
- Each character is **11 bytes** (one byte per row)
- Each byte represents **8 horizontal pixels**
- Display is **11 pixels tall** × **8 pixels wide** per character
- **1** = LED ON, **0** = LED OFF

#### Hex to Binary Example

The letter **'A'** is stored as:
```python
0x00, 0x38, 0x6c, 0xc6, 0xc6, 0xfe, 0xc6, 0xc6, 0xc6, 0xc6, 0x00
```

Converting each hex byte to binary (8 pixels):
```
0x00 = 00000000  →          (empty row)
0x38 = 00111000  →    ███   
0x6c = 01101100  →   ██ ██  
0xc6 = 11000110  →  ██   ██ 
0xc6 = 11000110  →  ██   ██ 
0xfe = 11111110  →  ███████ 
0xc6 = 11000110  →  ██   ██ 
0xc6 = 11000110  →  ██   ██ 
0xc6 = 11000110  →  ██   ██ 
0xc6 = 11000110  →  ██   ██ 
0x00 = 00000000  →          (empty row)
```

#### Text-to-LED Pipeline

1. **Input**: User provides text string (e.g., "HELLO")
2. **Character Lookup**: Each character is mapped to its font data offset
3. **Bitmap Extraction**: 11 bytes retrieved per character from font data
4. **Buffer Assembly**: All character bitmaps concatenated into continuous buffer
5. **Protocol Header**: Added to buffer with display settings (speed, mode, brightness)
6. **USB Transfer**: Complete buffer sent to device in 64-byte chunks

#### Protocol Structure

The complete data buffer sent to the device:
```
[64-byte header][message 1 bitmap][message 2 bitmap]...[padding]
```

**Header contains**:
- Magic bytes (`wang`)
- Brightness setting (25%, 50%, 75%, 100%)
- Mode for each message (scroll, static, animation, etc.)
- Speed for each message (1-8)
- Special effects (blink, animated border)
- Message lengths
- Timestamp

#### Why Hexadecimal?

Hex is used because:
- **Compact**: `0xfe` is shorter than `11111110`
- **Readable**: Easier to recognize patterns than long binary strings
- **Standard**: Common format for low-level data representation

### Example: Displaying "HI"

```python
from led_fun import SimpleTextAndIcons, LedNameBadge
from array import array

# Create font handler
font = SimpleTextAndIcons()

# Convert "HI" to bitmap
bitmap, width = font.bitmap_text("HI")
# Returns: 22 bytes (11 for 'H' + 11 for 'I')

# Create protocol header
header = LedNameBadge.header(
    lengths=[width],
    speeds=[4],
    modes=[0],
    blinks=[0],
    ants=[0],
    brightness=100
)

# Assemble and send
buf = array('B')
buf.extend(header)
buf.extend(bitmap)
LedNameBadge.write(buf)
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
led-fun = "led_fun.cli:cli_entry"
```

This allows the `led-fun` command to be available after installation.

### Using as a Library

You can also use led-fun as a Python library in your own projects:

```python
from led_fun import SimpleTextAndIcons, LedNameBadge
from array import array

# Create message
font = SimpleTextAndIcons()
bitmap, width = font.bitmap_text("Hello!")

# Send to device
header = LedNameBadge.header([width], [4], [0], [0], [0], brightness=100)
buf = array('B')
buf.extend(header)
buf.extend(bitmap)
LedNameBadge.write(buf)
```

## License

See [LICENSE](LICENSE) file for details.
