import sys
import os
import time

from dotenv import load_dotenv
from pyicloud.services.drive import DriveNode
from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer
from shutil import copyfileobj
from pyicloud import PyiCloudService

load_dotenv()

ICLOUD_PASSWORD = os.getenv("PASSWORD")
ICLOUD_EMAIL = os.getenv("EMAIL")
api = PyiCloudService(ICLOUD_EMAIL, ICLOUD_PASSWORD)

if api.requires_2fa:
    code = input("Enter the code you received of one of your approved devices: ")
    result = api.validate_2fa_code(code)
    print("Code validation result: %s" % result)

    if not result:
        print("Failed to verify security code")
        sys.exit(1)

    if not api.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result: bool = api.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print(
                "Failed to request trust. You will likely be prompted for the code again in the coming weeks"
            )
elif api.requires_2sa:
    import click

    print("Two-step authentication required. Your trusted devices are:")

    devices = api.trusted_devices
    for i, device in enumerate(devices):
        print(
            "  %s: %s"
            % (i, device.get("deviceName", "SMS to %s" % device.get("phoneNumber")))
        )

    device: devices = click.prompt("Which device would you like to use?", default=0)
    device: devices = devices[device]
    if not api.send_verification_code(device):
        print("Failed to send verification code")
        sys.exit(1)

    code = click.prompt("Please enter validation code")
    if not api.validate_verification_code(device, code):
        print("Failed to verify verification code")
        sys.exit(1)


obsidian_folder: DriveNode | None = api.drive["Documents"]

obsidian_folder: DriveNode | None = (
    obsidian_folder["Obsidian Vault"] if obsidian_folder is not None else None
)


if obsidian_folder is not None:

    def folder_enum(folder, path) -> None:
        for item in folder.dir():
            if folder[item].type == "folder":
                print(item, "Folder")
                os.makedirs(os.path.join(path, item), exist_ok=True)
                folder_enum(folder[item], os.path.join(path, item))

            if folder[item].type == "file":
                with folder[item].open(stream=True) as response:
                    with open(os.path.join(path, item), "wb") as file:
                        copyfileobj(response.raw, file)

    path = "obsidian"
    os.makedirs(path, exist_ok=True)
    folder_enum(obsidian_folder, path)

    class MyEventHandler(FileSystemEventHandler):
        def on_any_event(self, event: FileSystemEvent) -> None:
            print(event)

    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()

