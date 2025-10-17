#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""Command-line interface for LED badge control.

This module provides the CLI commands for uploading messages and graphics
to LED badges via USB.
"""

import re
from array import array
from typing import List, Optional

import typer

from led_fun.font import SimpleTextAndIcons
from led_fun.device import LedNameBadge


def split_to_ints(list_str: str) -> List[int]:
    """Split a comma or space-separated string into a list of integers.
    
    Args:
        list_str: String containing numbers separated by commas or spaces
        
    Returns:
        List of integers
        
    Example:
        "1,2,3" -> [1, 2, 3]
        "1 2 3" -> [1, 2, 3]
    """
    return [int(x) for x in re.split(r'[\s,]+', list_str)]


def main(
    message: List[str] = typer.Argument(
        None,
        help="Up to 8 message texts with embedded builtin icons or loaded images within colons(:)"
    ),
    speed: str = typer.Option(
        "4", 
        "--speed", 
        "-s",
        help="Scroll speed (Range 1..8). Up to 8 comma-separated values."
    ),
    brightness: int = typer.Option(
        100, 
        "--brightness", 
        "-B",
        help="Brightness for the display in percent: 25, 50, 75, or 100."
    ),
    mode: str = typer.Option(
        "0", 
        "--mode", 
        "-m",
        help="Up to 8 mode values: Scroll-left(0) -right(1) -up(2) -down(3); still-centered(4); animation(5); drop-down(6); curtain(7); laser(8)"
    ),
    blink: str = typer.Option(
        "0", 
        "--blink", 
        "-b",
        help="1: blinking, 0: normal. Up to 8 comma-separated values."
    ),
    ants: str = typer.Option(
        "0", 
        "--ants", 
        "-a",
        help="1: animated border, 0: normal. Up to 8 comma-separated values."
    ),
    preload: Optional[List[str]] = typer.Option(
        None, 
        "--preload", 
        "-p",
        help="Load bitmap images (deprecated, embed within ':' instead)"
    ),
    list_icons: bool = typer.Option(
        False,
        "--list-icons",
        "-l",
        help="List named icons to be embedded in messages and exit"
    ),
) -> None:
    """Upload messages or graphics to a 11x44 LED badge via USB.
    
    This tool allows you to display custom text, animations, and icons
    on LED badge devices connected via USB.
    
    Example combining image and text:
        led-fun 'I:ball:you'
    
    Display modes:
        0: Scroll-left (default)
        1: Scroll-right
        2: Scroll-up
        3: Scroll-down
        4: Still-centered
        5: Animation
        6: Drop-down
        7: Curtain
        8: Laser
    """
    if list_icons:
        icons = SimpleTextAndIcons._get_named_bitmaps_keys()
        typer.echo("Available named icons:")
        typer.echo(":" + ":  :".join(icons) + ":")
        typer.echo("\nOr use custom images: :path/to/some_icon.png:")
        raise typer.Exit()
    
    if not message:
        typer.echo("Error: Missing required argument 'MESSAGE'.")
        typer.echo("Try 'led-fun --help' for help.")
        raise typer.Exit(1)
    
    creator = SimpleTextAndIcons()

    if preload:
        for filename in preload:
            creator.add_preload_img(filename)

    msg_bitmaps = []
    for msg_arg in message:
        msg_bitmaps.append(creator.bitmap(msg_arg))

    lengths = [b[1] for b in msg_bitmaps]
    speeds = split_to_ints(speed)
    modes = split_to_ints(mode)
    blinks = split_to_ints(blink)
    ants_vals = split_to_ints(ants)

    buf = array('B')
    buf.extend(LedNameBadge.header(lengths, speeds, modes, blinks, ants_vals, brightness))

    for msg_bitmap in msg_bitmaps:
        buf.extend(msg_bitmap[0])

    LedNameBadge.write(buf)


def cli_entry() -> None:
    """Entry point for the CLI application."""
    typer.run(main)


if __name__ == '__main__':
    cli_entry()

