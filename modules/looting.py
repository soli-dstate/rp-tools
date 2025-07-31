import sys
import os
import logging
import json
import random
import commondefs
import base64

version = "1.0.0"
displayname = "Looting"

requirements = ["inventorymanager.py"]

logger = logging.getLogger(__name__)

modules_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules'))
if not os.path.exists(modules_dir):
    os.makedirs(modules_dir)
for req in requirements:
    req_path = os.path.join(modules_dir, req)
    if not os.path.exists(req_path):
        logger.error(f"required module {req} not found in {modules_dir}. please ensure it is installed.")
        break

persistentdata = False
savefile = False

debug = False

tables_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tables'))
if not os.path.exists(tables_dir):
    os.makedirs(tables_dir)

currenttable = None
currenttable_name = None
currenttable_description = None
currenttable_uuid = None
currenttable_rarities = None
currenttable_content = None

current_inventory = []
selected_character = None
currency = 0
current_storage = []
saved_characters = []
saved_inventories = []
saved_storage = []
freeslots = 10

saves_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saves'))
mainsave = os.path.join(saves_dir, 'mainsave.lsfv')
persistentdata_path = os.path.join(saves_dir, 'persistent_data.lsfv')

with open(mainsave, 'rb') as f:
    raw = f.read()
    if raw:
        decoded = base64.b85decode(raw).decode('utf-8')
        mdata = json.loads(decoded)
        current_inventory = mdata.get('inventory', [])
        selected_character = mdata.get('selected_character', None)
        currency = mdata.get('currency', 0)
        current_storage = mdata.get('storage', [])
        saved_characters = mdata.get('saved_characters', [])
        saved_inventories = mdata.get('saved_inventories', [])
        saved_storage = mdata.get('saved_storage', [])
        freeslots = mdata.get('freeslots', 10)
        if debug == True:
            logger.info(f"loaded mainsave: {mdata}")
            logger.info(f"current_inventory: {current_inventory}")
            logger.info(f"selected_character: {selected_character}")
            logger.info(f"currency: {currency}")
            logger.info(f"current_storage: {current_storage}")
            logger.info(f"saved_characters: {saved_characters}")
            logger.info(f"saved_inventories: {saved_inventories}")
            logger.info(f"saved_storage: {saved_storage}")

try:
    if os.path.exists(persistentdata_path):
        with open(persistentdata_path, 'rb') as f:
            raw = f.read()
            if raw:
                decoded = base64.b85decode(raw).decode('utf-8')
                pdata = json.loads(decoded)
                default_uuid = pdata.get('default_table_uuid')
                if default_uuid:
                    table_files = [f for f in os.listdir(tables_dir) if f.endswith('.json')]
                    for fname in table_files:
                        table_path = os.path.join(tables_dir, fname)
                        with open(table_path, 'r', encoding='utf-8') as tf:
                            tdata = json.load(tf)
                            if tdata.get('uuid') == default_uuid:
                                currenttable_name = fname
                                currenttable_description = tdata.get('description', 'No description available.')
                                currenttable_uuid = tdata.get('uuid', 'No UUID available.')
                                currenttable = tdata.get('content', [])
                                currenttable_rarities = tdata.get('rarities', {})
                                currenttable_content = tdata
                                logger.info(f"loaded default table: {currenttable_name}")
                                break
except Exception as e:
    logger.error(f"error loading default table: {e}")

if not os.path.exists(mainsave):
    logger.error(f"main save file {mainsave} does not exist.")
else:
    savefile = True

if not os.path.exists(persistentdata_path):
    logger.error(f"persistent data file {persistentdata_path} does not exist.")
    persistentdata_exists = False
else:
    persistentdata_exists = True

def get_random_item(table):
    rarity_weights = {
        "common": 60,
        "uncommon": 25,
        "rare": 10,
        "legendary": 4,
        "mythic": 1
    }
    total_weight = sum(rarity_weights[item["rarity"].lower()] for item in table)
    random_weight = random.randint(1, total_weight)
    cumulative_weight = 0
    for item in table:
        cumulative_weight += rarity_weights[item["rarity"].lower()]
        if random_weight <= cumulative_weight:
            quantity = random.randint(item["minrand"], item["maxrand"])
            item_copy = item.copy()
            item_copy["quantity"] = quantity
            return item_copy

def primary():
    logger.info(f"{displayname} module started successfully")
    global currenttable, currenttable_name, currenttable_description, currenttable_uuid, currenttable_content, currenttable_rarities, savefile, persistentdata
    if savefile == False or persistentdata == False:
        logger.error("a save file and/or persistent data file is required for this module to run. please create one using the inventorymanager.py module before running this module.")
    else:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            if not currenttable:
                print("No table loaded.")
                tableopts = ["Load a table", "Exit"]
                commondefs.print_menu(tableopts)
                result = input("Select an option: ").strip()
                if result == "1":
                    table_files = [f for f in os.listdir(tables_dir) if f.endswith('.json')]
                    if not table_files:
                        print("No tables found in /tables.")
                        input("Press any key to exit...")
                        logger.info('exiting due to no tables in the tables folder')
                        break
                    else:
                        print("Available tables:")
                        for idx, fname in enumerate(table_files, 1):
                            print(f"{idx}. {fname}")
                        try:
                            user_input = input("Select a table to load (or type 'exit' to exit): ").strip()
                            if user_input.lower() == 'exit':
                                print("Exiting...")
                                logger.info('program exited by user choice')
                                break
                            choice = int(user_input) - 1
                            if 0 <= choice < len(table_files):
                                currenttable_name = table_files[choice]
                                currenttable_path = os.path.join(tables_dir, currenttable_name)
                                with open(currenttable_path, 'r', encoding='utf-8') as f:
                                    currenttable_content = json.load(f)
                                    currenttable_description = currenttable_content.get('description', 'No description available.')
                                    currenttable_uuid = currenttable_content.get('uuid', 'No UUID available.')
                                    currenttable = currenttable_content.get('content', [])
                                    currenttable_rarities = currenttable_content.get('rarities', {})
                                    logger.info(f'loaded table {currenttable_name}')
                            else:
                                print("Invalid selection.")
                        except Exception as e:
                            print(f"Error: {e}")
                elif result == "2":
                    print("Exiting...")
                    logger.info('program exited by user choice')
                    break
            else:
                tableopts = ["Looting", "Table Management", "Exit"]
                commondefs.print_menu(tableopts)
                result = input("Select an option: ").strip()
                if result == "1":
                    if not currenttable:
                        print("No table loaded.")
                        input("Press any key to continue...")
                        continue
                    
                elif result == "2":
                    print(f"Current table: {currenttable_name}")
                    opts = ["Load new table", "View current table information", "Set current table as default", "Exit"]
                    commondefs.print_menu(opts)
                    choice = input("Select an option: ").strip()
                    if choice == "1":
                        table_files = [f for f in os.listdir(tables_dir) if f.endswith('.json')]
                        if not table_files:
                            print("No tables found in /tables.")
                            input("Press any key to exit...")
                            logger.info('exiting due to no tables in the tables folder')
                            break
                        else:
                            print("Available tables:")
                            for idx, fname in enumerate(table_files, 1):
                                print(f"{idx}. {fname}")
                            try:
                                user_input = input("Select a table to load (or type 'exit' to exit): ").strip()
                                if user_input.lower() == 'exit':
                                    print("Exiting...")
                                    logger.info('program exited by user choice')
                                    break
                                choice = int(user_input) - 1
                                if 0 <= choice < len(table_files):
                                    currenttable_name = table_files[choice]
                                    currenttable_path = os.path.join(tables_dir, currenttable_name)
                                    with open(currenttable_path, 'r', encoding='utf-8') as f:
                                        currenttable_content = json.load(f)
                                        currenttable_description = currenttable_content.get('description', 'No description available.')
                                        currenttable_uuid = currenttable_content.get('uuid', 'No UUID available.')
                                        currenttable = currenttable_content.get('content', [])
                                        currenttable_rarities = currenttable_content.get('rarities', {})
                                        logger.info(f'loaded table {currenttable_name}')
                                else:
                                    print("Invalid selection.")
                            except Exception as e:
                                print(f"Error: {e}")
                    elif choice == "2":
                        if currenttable:
                            print(f"Table Name: {currenttable_name}")
                            print(f"Description: {currenttable_description}")
                            print(f"UUID: {currenttable_uuid}")
                            print("Rarities:")
                            for rarity, weight in currenttable_rarities.items():
                                print(f"{rarity}: {weight}")
                        else:
                            print("No table loaded.")
                        input("Press any key to continue...")
                        if currenttable:
                            print(f"Current table is '{currenttable_name}'.")
                            confirm = input("Are you sure you want to set this as the default table? (y/n): ").strip().lower()
                            if confirm == 'y':
                                try:
                                    if os.path.exists(persistentdata_path):
                                        with open(persistentdata_path, 'rb') as f:
                                            raw = f.read()
                                            if raw:
                                                decoded = base64.b85decode(raw).decode('utf-8')
                                                data = json.loads(decoded)
                                            else:
                                                data = {}
                                    else:
                                        data = {}
                                    data['default_table_uuid'] = currenttable_uuid
                                    encoded = base64.b85encode(json.dumps(data, indent=4).encode('utf-8'))
                                    with open(persistentdata_path, 'wb') as f:
                                        f.write(encoded)
                                    print("Default table set successfully.")
                                    logger.info(f"set default table UUID to {currenttable_uuid}")
                                except Exception as e:
                                    print(f"Failed to set default table: {e}")
                                    logger.error(f"failed to set default table: {e}")
                            else:
                                print("Operation cancelled.")