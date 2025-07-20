import os
import datetime
import threading
import sys
import traceback

version = "1.0.0"

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
    f.write(f'Log file created at {now_str}\n')

currentlog = log_path

def exception_logger(exc_type, exc_value, exc_traceback):
    with open(currentlog, 'a') as f:
        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ')
        f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

def exception_thread():
    sys.excepthook = exception_logger

thread = threading.Thread(target=exception_thread, daemon=True)
thread.start()

def main():
    with open(currentlog, 'a') as f:
        f.write(f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] main thread started\n')
    

main()
