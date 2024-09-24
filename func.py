from watchdog.observers import Observer
from watchdog.events import (
    DirModifiedEvent,
    FileModifiedEvent,
    FileSystemEventHandler,
    DirCreatedEvent,
    FileCreatedEvent,
    DirDeletedEvent,
    FileDeletedEvent,
)


class MyHandler(FileSystemEventHandler):
    def on_created(self, event: DirCreatedEvent | FileCreatedEvent) -> None:
        pass

    def on_deleted(self, event: DirDeletedEvent | FileDeletedEvent) -> None:
        pass

    def on_modified(self, event: DirModifiedEvent | FileModifiedEvent) -> None:
        print(f"File {event.src_path} has been modified!")


# Create observer and event handler
observer = Observer()
event_handler = MyHandler()

# Set up observer to watch a specific directory
directory_to_watch = "."
observer.schedule(event_handler, directory_to_watch, recursive=True)

# Start the observer
observer.start()

# Keep the script running
try:
    while True:
        pass
except KeyboardInterrupt:
    observer.stop()

observer.join()
