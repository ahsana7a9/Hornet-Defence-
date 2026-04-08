import os
import psutil
import time
from core.scanner import scan_system

def get_usb_drives():
    drives = []

    partitions = psutil.disk_partitions()

    for p in partitions:
        if 'removable' in p.opts:
            drives.append(p.device)

    return drives


def monitor_usb():

    print("USB Monitoring Started...")

    known_drives = set(get_usb_drives())

    while True:

        time.sleep(5)

        current_drives = set(get_usb_drives())

        # detect new USB
        new_drives = current_drives - known_drives

        if new_drives:
            for drive in new_drives:
                print(f"USB Inserted: {drive}")

                print("Starting Scan...")
                results = scan_usb(drive)

                print("Scan Complete:", results)

        known_drives = current_drives


def scan_usb(drive_path):

    results = []

    for root, dirs, files in os.walk(drive_path):

        for file in files:

            full_path = os.path.join(root, file)

            results.append(full_path)

            if len(results) > 50:
                return results

    return results
