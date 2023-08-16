import os
import shutil
import datetime #log file timestamps
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
    
# def wait_for_download(path, file, dl_size_bottom=1):
#     dl_size_top = os.path.getsize(os.path.join(path, file))
#     if dl_size_top == dl_size_bottom:
#         return True
#     else:
#         time.sleep(.5)
#         wait_for_download(path, file, dl_size_top)    

def wait_for_download(file):
    size_bottom = -1
    try:
        while True:
            if size_bottom != os.path.getsize(os.path.join(get_os_download_path(), file)):
                size_bottom = os.path.getsize(os.path.join(get_os_download_path(), file))
                time.sleep(1)
    except FileNotFoundError:
        return True
        
        



def sort_files():
    path = get_os_download_path()
    with os.scandir(path) as it:
        for entry in it:
            ext = os.path.splitext(entry.name)[-1][1:].upper() #get file extension without "." and convert to uppercase
            if entry.name.endswith('.crdownload') or entry.name.endswith('.tmp') or entry.name.endswith('.part'):
                wait_for_download(entry.name)==True
            if not entry.name.startswith('.') and entry.is_file() and entry.name!='desktop.ini' and entry.name!='log.txt' and not entry.name.endswith('.crdownload') and not entry.name.endswith('.tmp') and not entry.name.endswith('.part'):
                try:
                    ext_dest = os.path.join(path, ext)
                    os.makedirs(ext_dest, exist_ok=True)
                    shutil.move(os.path.join(path, entry.name), os.path.join(ext_dest, entry.name)) #copyfile() is most optimized for windows
                except PermissionError:
                    time.sleep(3)
                # except:
                #     ext_dest = os.path.join(path, ext, entry.name)
                #     # os.makedirs(ext_dest, exist_ok=True)
                #     os.replace(entry.name, ext_dest)

class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')  # 2020-04-30 16:09:32
        log_info = f'{formatted_time} - event type: {event.event_type}  src_path: {event.src_path}\n'
        if event.src_path.endswith('log.txt')==False:
            with open(os.path.join(get_os_download_path(),'log.txt'), 'a+') as log_file:
                log_file.write(log_info)
            print(log_info)
    def on_created(self, event):
        sort_files()
    # def on_deleted(self, event, marker=1):
    #     print(log)   
    # def on_modified(self, event):
    #     print(log)
    

def start_observer():
    path = get_os_download_path()
    event_handler = MyHandler()
    observer = observers.Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

start_observer()



