import os
import shutil
from watchdog import observers
from watchdog.events import FileSystemEventHandler
import time


def get_os_download_path():
    """Returns the default downloads path for linux or windows"""
    if os.name == 'nt':
        from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx 
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with OpenKey(HKEY_CURRENT_USER, sub_key) as key:
            location = QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')
    
def sort_files():
    path = get_os_download_path()
    with os.scandir(path) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                ext = os.path.splitext(entry.name)[-1][1:].upper() #get file extension without "." and convert to uppercase
                try:
                    ext_dest = os.path.join(path, ext)
                    os.makedirs(ext_dest, exist_ok=True)
                    shutil.move(entry.name, ext_dest) #copyfile() is most optimized for windows
                except:
                    ext_dest = os.path.join(path, ext, entry.name)
                    # os.makedirs(ext_dest, exist_ok=True)
                    os.replace(entry.name, ext_dest)

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        # sort_files()
        print(f'event type: {event.event_type}  path : {event.src_path}')

def start_observer():
    path = get_os_download_path()
    event_handler = MyHandler()
    observer = observers.Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

start_observer()



