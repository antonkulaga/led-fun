"""LED Badge Control Library.

A Python library for controlling LED badge displays via USB.
Supports text, icons, animations, and various display modes.
"""

from led_fun.font import SimpleTextAndIcons
from led_fun.device import LedNameBadge, WriteLibUsb
from led_fun.cli import cli_entry, main

__all__ = [
    "SimpleTextAndIcons",
    "LedNameBadge",
    "WriteLibUsb",
    "cli_entry",
    "main",
]
