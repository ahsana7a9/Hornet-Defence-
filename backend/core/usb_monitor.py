import psutil
import time
import os

def get_usb_drives():
    drives = []
    for p in psutil.disk_partitions():
        if 'removable' in p.opts:
            drives.append(p.device)
    return drives


def scan_usb(drive_path):
    results = []

    for root, dirs, files in os.walk(drive_path):
        for file in files:
            results.append(os.path.join(root, file))

            if len(results) > 50:
                return results

    return results


def monitor_usb_with_callback(callback):

    print("USB Monitoring Started...")

    known = set(get_usb_drives())

    while True:
        time.sleep(5)

        current = set(get_usb_drives())
        new = current - known

        if new:
            for drive in new:
                print(f"USB Inserted: {drive}")

                results = scan_usb(drive)

                callback(results)

        known = current
