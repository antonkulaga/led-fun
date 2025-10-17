#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""USB device communication for LED badge.

This module handles low-level USB communication with LED badge devices
using pyusb and libusb. It includes protocol header generation and
data transmission logic.
"""

import sys
import time
from array import array
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class WriteLibUsb:
    """Write to a device using pyusb and libusb.
    
    The device ids consist of the bus number, the device number on that bus
    and the endpoint number.
    """
    _module_loaded = False
    try:
        import usb.core
        import usb.util
        _module_loaded = True
        print("Module usb.core detected")
    except:
        pass

    def __init__(self):
        self.devices: Dict[str, Tuple] = {}
        self.description: Optional[str] = None
        self.dev = None
        self.endpoint = None

    def get_name(self) -> str:
        """Get the name of this write method."""
        return 'libusb'

    def get_description(self) -> str:
        """Get a description of this write method."""
        return 'Program a device connected via USB using the pyusb package and libusb.'

    def open(self, device_id: str) -> bool:
        """Open communication channel to the device.
        
        Similar to opening a file. The device id is one of the ids
        returned by get_available_devices() or 'auto', which selects
        just the first device in that dict.
        
        Args:
            device_id: Device identifier or 'auto'
            
        Returns:
            True if successfully opened, False otherwise
        """
        if self.is_ready() and self.is_device_present():
            actual_device_id = None
            if device_id == 'auto':
                actual_device_id = sorted(self.devices.keys())[0]
            else:
                if device_id in self.devices.keys():
                    actual_device_id = device_id

            if actual_device_id:
                return self._open(actual_device_id)
        return False

    def is_device_present(self) -> bool:
        """Check if devices are available.
        
        Returns:
            True if one or more devices are available, False otherwise
        """
        self.get_available_devices()
        return self.devices and len(self.devices) > 0

    def _open(self, device_id: str) -> bool:
        """Internal method to open a specific device."""
        self.description = self.devices[device_id][0]
        self.dev = self.devices[device_id][1]
        self.endpoint = self.devices[device_id][2]
        print("Libusb device initialized")
        return True

    @staticmethod
    def add_padding(buf: array, block_size: int) -> None:
        """Extend data array with zeros to align with block size.
        
        After calling this, the length of the array will be a multiple of block_size.
        
        Args:
            buf: Data array to pad
            block_size: Desired block size for alignment
        """
        need_padding = len(buf) % block_size
        if need_padding:
            buf.extend((0,) * (block_size - need_padding))

    @staticmethod
    def check_length(buf: array, max_size: int) -> None:
        """Check if data array exceeds maximum size.
        
        Aborts program execution if buffer is too large to prevent
        damaging the display.
        
        Args:
            buf: Data array to check
            max_size: Maximum allowed size in bytes
        """
        if len(buf) > max_size:
            print(f"Writing more than {max_size} bytes damages the display! Nothing written.")
            sys.exit(1)

    def close(self) -> None:
        """Close the device connection and clean up resources."""
        if self.dev:
            self.dev.reset()
            WriteLibUsb.usb.util.dispose_resources(self.dev)
        self.description = None
        self.dev = None
        self.endpoint = None

    def write(self, buf: array) -> None:
        """Write data to the opened device.
        
        Args:
            buf: Data buffer to write
        """
        self.add_padding(buf, 64)
        self.check_length(buf, 8192)
        self._write(buf)

    def get_available_devices(self) -> Dict[str, str]:
        """Get all devices available via this write method.
        
        Returns:
            Dict with device ids as keys and device descriptions as values
        """
        if self.is_ready() and not self.devices:
            self.devices = self._get_available_devices()
        return {did: data[0] for did, data in self.devices.items()}

    def _get_available_devices(self) -> Dict[str, Tuple]:
        """Internal method to scan for available USB devices."""
        devs = WriteLibUsb.usb.core.find(idVendor=0x0416, idProduct=0x5020, find_all=True)
        devices = {}
        for d in devs:
            try:
                # win32: NotImplementedError: is_kernel_driver_active
                if d.is_kernel_driver_active(0):
                    d.detach_kernel_driver(0)
            except:
                pass
            try:
                d.set_configuration()
            except WriteLibUsb.usb.core.USBError:
                print("No read access to device list!")
                LedNameBadge._print_sudo_hints()
                sys.exit(1)

            cfg = d.get_active_configuration()[0, 0]
            eps = WriteLibUsb.usb.util.find_descriptor(
                cfg,
                find_all=True,
                custom_match=lambda e: WriteLibUsb.usb.util.endpoint_direction(e.bEndpointAddress) == WriteLibUsb.usb.util.ENDPOINT_OUT)
            for ep in eps:
                did = "%d:%d:%d" % (d.bus, d.address, ep.bEndpointAddress)
                descr = ("%s - %s (bus=%d dev=%d endpoint=%d)" %
                         (d.manufacturer, d.product, d.bus, d.address, ep.bEndpointAddress))
                devices[did] = (descr, d, ep)
        return devices

    def is_ready(self) -> bool:
        """Check if the USB module is loaded and ready."""
        return WriteLibUsb._module_loaded

    def has_device(self) -> bool:
        """Check if a device is currently opened."""
        return self.dev is not None

    def _write(self, buf: array) -> None:
        """Internal method to perform the actual USB write."""
        if not self.dev:
            return

        try:
            # win32: NotImplementedError: is_kernel_driver_active
            if self.dev.is_kernel_driver_active(0):
                self.dev.detach_kernel_driver(0)
        except:
            pass

        try:
            self.dev.set_configuration()
        except WriteLibUsb.usb.core.USBError:
            print("No write access to device!")
            LedNameBadge._print_sudo_hints()
            sys.exit(1)

        print(f"Write using {self.description} via libusb")
        for i in range(int(len(buf) / 64)):
            time.sleep(0.1)
            self.endpoint.write(buf[i * 64:i * 64 + 64])


class LedNameBadge:
    """High-level interface for LED badge communication.
    
    This class handles protocol header generation and coordinates
    the USB communication for displaying messages on LED badges.
    """
    
    _protocol_header_template = (
        0x77, 0x61, 0x6e, 0x67, 0x00, 0x00, 0x00, 0x00, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40, 0x40,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    )

    @staticmethod
    def header(
        lengths: List[int],
        speeds: List[int],
        modes: List[int],
        blinks: List[int],
        ants: List[int],
        brightness: int = 100,
        date: datetime = datetime.now()
    ) -> List[int]:
        """Create a protocol header for LED badge communication.
        
        Args:
            lengths: Number of chars/byte-columns for each text/bitmap
            speeds: Scroll speeds (1-8) for each message
            modes: Display modes (0-8) for each message:
                0: Scroll-left, 1: Scroll-right, 2: Scroll-up, 3: Scroll-down,
                4: Still-centered, 5: Animation, 6: Drop-down, 7: Curtain, 8: Laser
            blinks: Blinking flag (0 or 1) for each message
            ants: Animated border flag (0 or 1) for each message
            brightness: Display brightness (25, 50, 75, or 100 percent)
            date: Timestamp to embed in header (not displayed on device)
            
        Returns:
            Protocol header as list of bytes
            
        Raises:
            TypeError: If parameters are not iterable or date is not datetime
            ValueError: If lengths sum is too high
        """
        try:
            lengths_sum = sum(lengths)
        except:
            raise TypeError(f"Please give a list or tuple with at least one number: {lengths}")
        if lengths_sum > (8192 - len(LedNameBadge._protocol_header_template)) / 11 + 1:
            raise ValueError(f"The given lengths seem to be far too high: {lengths}")

        ants = LedNameBadge._prepare_iterable(ants, 0, 1)
        blinks = LedNameBadge._prepare_iterable(blinks, 0, 1)
        speeds = LedNameBadge._prepare_iterable(speeds, 1, 8)
        modes = LedNameBadge._prepare_iterable(modes, 0, 8)

        speeds = [x - 1 for x in speeds]

        h = list(LedNameBadge._protocol_header_template)

        if brightness <= 25:
            h[5] = 0x40
        elif brightness <= 50:
            h[5] = 0x20
        elif brightness <= 75:
            h[5] = 0x10
        # else default 100% == 0x00

        for i in range(8):
            h[6] += blinks[i] << i
            h[7] += ants[i] << i

        for i in range(8):
            h[8 + i] = 16 * speeds[i] + modes[i]

        for i in range(len(lengths)):
            h[17 + (2 * i) - 1] = lengths[i] // 256
            h[17 + (2 * i)] = lengths[i] % 256

        try:
            h[38 + 0] = date.year % 100
            h[38 + 1] = date.month
            h[38 + 2] = date.day
            h[38 + 3] = date.hour
            h[38 + 4] = date.minute
            h[38 + 5] = date.second
        except:
            raise TypeError(f"Please give a datetime object: {date}")

        return h

    @staticmethod
    def _prepare_iterable(iterable: List[int], min_: int, max_: int) -> Tuple[int, ...]:
        """Prepare and validate an iterable of values.
        
        Clamps values to min/max range and pads to 8 elements by repeating last value.
        
        Args:
            iterable: List of values to prepare
            min_: Minimum allowed value
            max_: Maximum allowed value
            
        Returns:
            Tuple of exactly 8 values
            
        Raises:
            TypeError: If iterable is not valid
        """
        try:
            iterable = [min(max(x, min_), max_) for x in iterable]
            iterable = tuple(iterable) + (iterable[-1],) * (8 - len(iterable))  # repeat last element
            return iterable
        except:
            raise TypeError(f"Please give a list or tuple with at least one number: {iterable}")

    @staticmethod
    def _print_sudo_hints() -> None:
        """Print helpful hints about USB permissions."""
        print("\nTip: On Linux, you may need to set up udev rules for USB access.")
        print("Run: ./bin/setup_usb_permissions.sh")
        print("Or temporarily use: sudo")

    @staticmethod
    def write(buf: array) -> None:
        """Write the given buffer to the LED badge device.
        
        The buffer must begin with a protocol header as provided by header()
        followed by the bitmap data. The bitmap data is organized in bytes
        with 8 horizontal pixels per byte and 11 bytes per (8 pixels wide)
        byte-column.
        
        Args:
            buf: Complete data buffer including header and bitmap data
        """
        write_method = WriteLibUsb()
        write_method.open('auto')
        write_method.write(buf)
        write_method.close()

