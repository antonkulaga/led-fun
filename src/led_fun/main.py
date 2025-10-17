import usb.core
import usb.util

def get_available_devices():
    devices = {}
    devs = usb.core.find(idVendor=0x0416, idProduct=0x5020, find_all=True)

    for d in devs:
        cfg = d.get_active_configuration()[0, 0]
        eps = usb.util.find_descriptor(cfg, find_all=True, 
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
        for ep in eps:
            did = "%d:%d:%d" % (d.bus, d.address, ep.bEndpointAddress)
            descr = ("%s - %s (bus=%d dev=%d endpoint=%d)" % 
                (d.manufacturer, d.product, d.bus, d.address, ep.bEndpointAddress))
            devices[did] = (descr, d, ep)
    return devices


def main():
    devs = get_available_devices()
    if (len(devs) == 0):
        print("No device found")
        return

if __name__ == "__main__":
    main()