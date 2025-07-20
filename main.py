import os
import datetime
import threading
import sys
import traceback
import requests
import re

version = "1.0.0"

prerelease = False

folders = ['./saves', './modules', './logs']
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

logs_folder = './logs'
log_files = [f for f in os.listdir(logs_folder) if f.startswith('log') and f.endswith('.log')]
now_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

if not log_files:
    log_number = 0
else:
    log_numbers = [
        int(f.split('_')[0][3:]) for f in log_files
        if f.split('_')[0][3:].isdigit()
    ]
    log_number = max(log_numbers) + 1 if log_numbers else 0

log_filename = f'log{log_number}_{now_str}.log'
log_path = os.path.join(logs_folder, log_filename)
with open(log_path, 'w') as f:
    f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [INFO] log file created, main.py version is {version}\n')
    if getattr(sys, 'frozen', False):
        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [INFO] running as a compiled executable\n')
    else:
        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [INFO] running as an uncompiled python file\n')

currentlog = log_path

def exception_logger(exc_type, exc_value, exc_traceback):
    with open(currentlog, 'a') as f:
        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [ERROR] ')
        f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

def exception_thread():
    sys.excepthook = exception_logger

thread = threading.Thread(target=exception_thread, daemon=True)
thread.start()

def updater():
    with open(currentlog, 'a') as f:
        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [INFO] updater function initialized\n')
    repo_url = "https://raw.githubusercontent.com/soli-dstate/rp-tools/main/main.py"
    try:
        response = requests.get(repo_url, timeout=5)
        if response.status_code == 200:
            match = re.search(r'version\s*=\s*["\']([\d\.]+)["\']', response.text)
            if match:
                repo_version = match.group(1)
                def version_tuple(v):
                    return tuple(map(int, v.split(".")))
                local_version = version_tuple(version)
                remote_version = version_tuple(repo_version)
                if local_version > remote_version:
                    global prerelease
                    prerelease = True
                    with open(currentlog, 'a') as f:
                        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [INFO] local version ({version}) is newer than repo version ({repo_version}), marking as prerelease\n')
                elif local_version < remote_version:
                    print(f"A newer version ({repo_version}) is available. Please update.")
                    with open(currentlog, 'a') as f:
                        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [INFO] update available: repo version ({repo_version}) is newer than local version ({version})\n')
                else:
                    with open(currentlog, 'a') as f:
                        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [INFO] local version matches repo version ({version})\n')
            else:
                with open(currentlog, 'a') as f:
                    f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [WARN] could not find version string in main.py on repo\n')
        else:
            with open(currentlog, 'a') as f:
                f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [WARN] failed to fetch repo, status code {response.status_code}\n')
    except Exception as e:
        with open(currentlog, 'a') as f:
            f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [ERROR] exception during version check: {e}\n')

def main():
    with open(currentlog, 'a') as f:
        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [INFO] main function initialized\n')
    updater()
    
main()
