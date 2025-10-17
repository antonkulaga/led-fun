#!/bin/bash
# Setup script for USB LED device permissions

set -e

echo "Setting up USB permissions for LED device (Vendor: 0x0416, Product: 0x5020)..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please run this script as a regular user (not with sudo)"
    echo "The script will prompt for sudo when needed"
    exit 1
fi

# Create udev rule
UDEV_RULE_FILE="/etc/udev/rules.d/99-led-device.rules"
UDEV_RULE='SUBSYSTEM=="usb", ATTRS{idVendor}=="0416", ATTRS{idProduct}=="5020", MODE="0666", GROUP="plugdev"'

echo "Creating udev rule at $UDEV_RULE_FILE..."
echo "$UDEV_RULE" | sudo tee "$UDEV_RULE_FILE" > /dev/null

# Add user to plugdev group if it exists
if getent group plugdev > /dev/null 2>&1; then
    echo "Adding user $USER to plugdev group..."
    sudo usermod -a -G plugdev "$USER"
    echo "User $USER added to plugdev group"
else
    echo "Note: plugdev group doesn't exist on your system (this is fine for MODE=0666)"
fi

# Reload udev rules
echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo ""
echo "✓ USB permissions setup complete!"
echo ""
echo "IMPORTANT: For group membership changes to take effect, you need to:"
echo "  1. Log out and log back in, OR"
echo "  2. Reboot your system, OR"
echo "  3. Run: sudo udevadm trigger"
echo ""
echo "Then, unplug and replug your LED device."
echo ""
echo "Checking if device is currently detected..."
if lsusb | grep -q "0416:5020"; then
    echo "✓ LED device detected by lsusb"
    echo "  Please unplug and replug the device for the new permissions to take effect."
else
    echo "⚠ LED device not detected. Make sure it's connected."
fi

