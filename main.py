import os
import datetime
import threading
import sys
import traceback
import requests
import logging
import random
from bs4 import BeautifulSoup

version = "0.0.0"

prerelease = False

uncompiled = False

updaterran = False

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
currentlog = log_path
    
logging.basicConfig(
    filename=currentlog,
    filemode='a',
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

loginit = [
    "haiii it's da logggg... da version is " + version,
    "killer looogg... killer log from san diego. i don't know what i am but i taste really good. i am a killer log! hello. i'll be your killer log for the evening. the version is " + version,
    "what if instead of being called a log, it was called a freak log, and instead of logging things, it told you that the version is " + version,
    "even if uu haavee, even if u need, i don't mean to stare, we don't have to breed, we can plant a house, we can build a tree, i don't even care, we can have the version " + version,
    "top of the morning to you laddies, my name is jacksepticeye and the version is " + version,
    "fun fact: one day we will all die, but also the version is " + version,
    "welcome back master nya nya!~ i have to tell you something very important! okay... here goes... the version is " + version,
    "500 errors. " + version,
    "wha- i'm not just some stupid log! i have feelings too! i can feel pain, i can feel love, i can feel fear, and i can also feel that the version is " + version,
    "this is an orwellian dystopia... it's so orwellian that the version is " + version,
    "i have so much aura, it's like over 9 billion... it's still not bigger than the version number, which is " + version,
    "meow meow meow meow meow meow meow meow meow meow meow meow meow " + version,
    "awnefuihawefuihawiufehwaefiuhauih2198h9fndsjkfsvasoiadad901jsaiofcjasoidjvn " + version,
    "repentforyoursinsrepentforyoursinsrepentforyoursinsrepentforyoursins " + version,
    "/gamemode " + version,
]

logger.info(random.choice(loginit))

if getattr(sys, 'frozen', False):
    logger.info('running as a compiled executable')
else:
    logger.info('running as an uncompiled python file')
    uncompiled = True
    logger.info('value of uncompiled is set to ' + str(uncompiled))

def exception_logger(exc_type, exc_value, exc_traceback):
    logger.error(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))

def exception_thread():
    sys.excepthook = exception_logger

thread = threading.Thread(target=exception_thread, daemon=True)
thread.start()

def updater():
    github_repo = "https://raw.githubusercontent.com/soli-dstate/rp-tools/main/"
    modules_dir = "./modules"
    main_local_path = os.path.join(os.path.dirname(__file__), "main.py")
    main_github_url = github_repo + "main.py"
    def extract_version(code):
        for line in code.splitlines():
            if line.strip().startswith("version"):
                parts = line.split("=")
                if len(parts) > 1:
                    return parts[1].strip().strip('"\'')
        return None
    try:
        with open(main_local_path, "r", encoding="utf-8") as f:
            local_main_code = f.read()
        local_main_version = extract_version(local_main_code)
        remote_main_code = requests.get(main_github_url).text
        remote_main_version = extract_version(remote_main_code)
    except Exception as e:
        print(f"Error checking main.py version: {e}")
        logger.error(f"error checking main.py version: {e}")
        return
    mismatches = []
    if local_main_version != remote_main_version:
        logger.warning(f"main.py version mismatch: local={local_main_version}, github={remote_main_version}")
    else:
        logger.info(f"main.py is up to date (version {local_main_version})")
    module_files = [f for f in os.listdir(modules_dir) if f.endswith('.py') and not f.startswith('__')]
    for mod_file in module_files:
        local_path = os.path.join(modules_dir, mod_file)
        remote_url = github_repo + f"modules/{mod_file}"
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                local_code = f.read()
            local_version = extract_version(local_code)
            remote_code = requests.get(remote_url).text
            remote_version = extract_version(remote_code)
            if local_version != remote_version:
                logger.warning(f"module {mod_file} version mismatch: local={local_version}, github={remote_version}")
            else:
                logger.info(f"module {mod_file} is up to date (version {local_version})")
        except Exception as e:
            logger.error(f"error checking module {mod_file}: {e}")
    if not mismatches:
        print("All files are up to date with GitHub.")
        logger.info("all files (main.py and modules) are up to date with GitHub.")
    else:
        logger.info(f"version mismatches found: {mismatches}")

def main():
    global updaterran
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        if not updaterran:
            try:
                updater()
                updaterran = True
            except Exception as e:
                logger.error(f'updater failed: {e}')
                print("Updater failed. Continuing without update.")
        logger.info('main function initialized')
        import importlib.util
        modules_dir = './modules'
        module_files = [f for f in os.listdir(modules_dir) if f.endswith('.py') and not f.startswith('__')]
        modules = []
        for file in module_files:
            path = os.path.join(modules_dir, file)
            spec = importlib.util.spec_from_file_location(file[:-3], path)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                displayname = getattr(mod, 'displayname', file[:-3])
                if hasattr(mod, 'hidden') and mod.hidden:
                    logger.info(f'skipping hidden module {displayname}')
                    continue
                logger.info(f'loading module {displayname} from {file}')
                modules.append((displayname, mod))
            except Exception as e:
                logger.error(f'failed to load module {file}: {e}')
        if not modules:
            print("No modules found in /modules.")
            resp = input("Would you like to download modules from the github repository? (y/n)")
        else:
            print("Available modules:")
            for idx, (name, _) in enumerate(modules):
                print(f"{idx+1}. {name}")
            try:
                user_input = input("Select a module to run (or type 'exit' to exit, or type 'modules' to view modules available on the github repository): ").strip()
                if user_input.lower() == 'exit':
                    print("Exiting...")
                    logger.info('program exited by user choice')
                    break
                elif user_input.lower() == 'modules':
                    repo_modules_url = "https://github.com/soli-dstate/rp-tools/tree/main/modules"
                    raw_base_url = "https://raw.githubusercontent.com/soli-dstate/rp-tools/main/modules/"
                    print("Fetching available modules from GitHub...")
                    try:
                        response = requests.get(repo_modules_url)
                        response.raise_for_status()
                        soup = BeautifulSoup(response.text, "html.parser")
                        files = [a.text for a in soup.find_all("a", class_="js-navigation-open Link--primary") if a.text.endswith(".py")]
                        if not files:
                            print("No Python modules found in the repository.")
                        else:
                            print("Modules available on GitHub:")
                            for idx, fname in enumerate(files):
                                print(f"{idx+1}. {fname}")
                            selection = input("Select a module to download (number), or type 'back' to return: ").strip()
                            if selection.lower() == "back":
                                pass
                            else:
                                try:
                                    sel_idx = int(selection) - 1
                                    if 0 <= sel_idx < len(files):
                                        mod_name = files[sel_idx]
                                        local_path = os.path.join(modules_dir, mod_name)
                                        remote_url = raw_base_url + mod_name
                                        print(f"Downloading {mod_name} from GitHub...")
                                        remote_code = requests.get(remote_url).text
                                        remote_version = None
                                        for line in remote_code.splitlines():
                                            if line.strip().startswith("version"):
                                                remote_version = line.split("=")[1].strip().strip('"\'')
                                                break
                                        local_version = None
                                        if os.path.exists(local_path):
                                            with open(local_path, "r", encoding="utf-8") as f:
                                                for line in f:
                                                    if line.strip().startswith("version"):
                                                        local_version = line.split("=")[1].strip().strip('"\'')
                                                        break
                                        def version_tuple(v):
                                            return tuple(map(int, (v.split("."))))
                                        if local_version and remote_version:
                                            if version_tuple(remote_version) > version_tuple(local_version):
                                                with open(local_path, "w", encoding="utf-8") as f:
                                                    f.write(remote_code)
                                                print(f"Module {mod_name} updated to version {remote_version}.")
                                            elif version_tuple(remote_version) == version_tuple(local_version):
                                                print(f"Module {mod_name} is already up to date (version {local_version}).")
                                            else:
                                                print(f"Local version ({local_version}) is newer than remote ({remote_version}). Not overwriting.")
                                        else:
                                            with open(local_path, "w", encoding="utf-8") as f:
                                                f.write(remote_code)
                                            print(f"Module {mod_name} downloaded.")
                                    else:
                                        print("Invalid selection.")
                                except Exception as e:
                                    print(f"Error: {e}")
                    except Exception as e:
                        print(f"Failed to fetch modules from GitHub: {e}")
                else:
                    choice = int(user_input) - 1
                    if 0 <= choice < len(modules):
                        print(f"Starting module: {modules[choice][0]}")
                        logger.info(f'starting module {modules[choice][0]}')
                        if hasattr(modules[choice][1], 'primary') and callable(getattr(modules[choice][1], 'primary')):
                            logger.info(f'calling primary function of module {modules[choice][0]}')
                            modules[choice][1].primary()
                        else:
                            print("Selected module does not have a callable 'primary' function.")
                            logger.warning(f'module {modules[choice][0]} does not have a callable primary function')
                    else:
                        print("Invalid selection.")
            except Exception as e:
                print(f"Error: {e}")
            input("Press any key to continue...")

main()
