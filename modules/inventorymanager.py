import sys
import os
import logging
import json
import base64
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
import commondefs

version = "1.0.0"
displayname = "Inventory Manager"

requirements = [""]

logger = logging.getLogger(__name__)

modules_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules'))
if not os.path.exists(modules_dir):
    os.makedirs(modules_dir)
for req in requirements:
    req_path = os.path.join(modules_dir, req)
    if not os.path.exists(req_path):
        logger.error(f"required module {req} not found in {modules_dir}. please ensure it is installed.")
        break

saves_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saves'))
if not os.path.exists(saves_dir):
    os.makedirs(saves_dir)

persistent_data_file = os.path.join(saves_dir, 'persistent_data.lsvf')
if not os.path.exists(persistent_data_file):
    with open(persistent_data_file, 'w') as f:
        f.write('{}')

mainsave = os.path.join(saves_dir, 'mainsave.lsvf')
if not os.path.exists(mainsave):
    uuid_str = str(uuid.uuid4())
    mainsave_data = {"uuid": uuid_str}
    encoded_mainsave = base64.b85encode(json.dumps(mainsave_data).encode('utf-8')).decode('utf-8')
    with open(mainsave, 'w') as f:
        f.write(encoded_mainsave)
    if os.path.exists(persistent_data_file):
        with open(persistent_data_file, 'r') as f:
            try:
                decoded = base64.b85decode(f.read().encode('utf-8')).decode('utf-8')
                data = json.loads(decoded)
            except Exception:
                data = {}
    else:
        data = {}
    indices = [int(k.split('_')[-1]) for k in data if k.startswith("mainsave_uuid_") and k.split('_')[-1].isdigit()]
    next_index = max(indices) + 1 if indices else 0
    data[f"mainsave_uuid_{next_index}"] = uuid_str
    with open(persistent_data_file, 'w') as f:
        f.write(base64.b85encode(json.dumps(data).encode('utf-8')).decode('utf-8'))

current_inventory = []
selected_character = None
currency = 0
current_storage = []
saved_characters = []
saved_inventories = []
saved_storage = []
freeslots = 10

def save_data():
    data = {
        'current_inventory': current_inventory,
        'selected_character': selected_character,
        'currency': currency,
        'current_storage': current_storage,
        'saved_characters': saved_characters,
        'saved_inventories': saved_inventories,
        'saved_storage': saved_storage,
        'freeslots': freeslots
    }
    logger.info("encoding data to base85")
    try:
        encoded_data = base64.b85encode(json.dumps(data).encode('utf-8')).decode('utf-8')
    except Exception as e:
        logger.error(f"failed to encode data: {e}")
        return
    logger.info("writing data to mainsave file")
    try:
        with open(mainsave, 'w') as f:
            f.write(encoded_data)
        logger.info("data written successfully")
    except Exception as e:
        logger.error(f"failed to write data to mainsave file: {e}")
        return
    
def load_data():
    logger.info("reading data from mainsave file")
    try:
        with open(mainsave, 'r') as f:
            encoded_data = f.read()
        logger.info("decoding data from base85")
        decoded_data = base64.b85decode(encoded_data.encode('utf-8')).decode('utf-8')
        data = json.loads(decoded_data)
        global current_inventory, selected_character, currency, current_storage, saved_characters, saved_inventories, saved_storage
        current_inventory = data.get('current_inventory', [])
        selected_character = data.get('selected_character', None)
        currency = data.get('currency', 0)
        current_storage = data.get('current_storage', 0)
        saved_characters = data.get('saved_characters', [])
        saved_inventories = data.get('saved_inventories', [])
        saved_storage = data.get('saved_storage', [])
        freeslots = data.get('freeslots', 10)
        logger.info("data loaded successfully")
    except Exception as e:
        logger.error(f"failed to load data: {e}")

def primary():
    logger.info(f"{displayname} module started successfully")
    try:
        load_data()
        logger.info("data loaded successfully")
    except Exception as e:
        logger.error(f"failed to load data: {e}")
        input("Error loading data. Please check the logs. Press any key to exit...")
        return
    while True:
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
            options = ["Character Management", "Inventory Management", "Storage Management", "Bank"]
            commondefs.print_menu(options)
            choice = input("Select an option (or type 'exit' to exit): ").strip().lower()
            if choice == "exit":
                logger.info("exiting inventory manager")
                break
            if choice == 1:
                os.system('cls' if os.name == 'nt' else 'clear')
                logger.info("selected character management")
                print("Character Management")
                options = ["Create Character", "View Characters", "Select Character", "Delete Character", "Back"]
                commondefs.print_menu(options)
                user_choice = input("Select an option: ").strip()
                if user_choice == 1:
                    logger.info("creating new character")
                    name = input("Enter character name: ").strip()
                    if not name:
                        print("Character name cannot be empty.")
                        continue
                    if name in saved_characters:
                        print(f"Character '{name}' already exists.")
                        continue
                    saved_characters.append(name)
                    print(f"Character '{name}' created successfully.")
                    try:
                        save_data()
                        logger.info("character data saved successfully")
                    except Exception as e:
                        logger.error(f"failed to save character data: {e}")
                        input("Error saving character data. Please check the logs. Press any key to continue...")
                if user_choice == 2:
                    logger.info("viewing characters")
                    if not saved_characters:
                        print("No characters available.")
                    else:
                        print("Saved Characters:")
                        for idx, char in enumerate(saved_characters, start=1):
                            print(f"{idx}. {char}")
                    input("Press any key to continue...")
                if user_choice == 3:
                    logger.info("selecting character")
                    if not saved_characters:
                        print("No characters available to select.")
                        continue
                    print("Select a character:")
                    for idx, char in enumerate(saved_characters, start=1):
                        print(f"{idx}. {char}")
                    char_choice = commondefs.get_user_choice(len(saved_characters))
                    selected_character = saved_characters[char_choice - 1]
                    print(f"Selected character: {selected_character}")
                    try:
                        save_data()
                        logger.info("selected character saved successfully")
                    except Exception as e:
                        logger.error(f"failed to save selected character: {e}")
                        input("Error saving selected character. Please check the logs. Press any key to continue...")
                if user_choice == 4:
                    logger.info("deleting character")
                    if not saved_characters:
                        print("No characters available to delete.")
                        continue
                    print("Select a character to delete:")
                    for idx, char in enumerate(saved_characters, start=1):
                        print(f"{idx}. {char}")
                    char_choice = commondefs.get_user_choice(len(saved_characters))
                    char_to_delete = saved_characters[char_choice - 1]
                    saved_characters.remove(char_to_delete)
                    print(f"Character '{char_to_delete}' deleted successfully.")
                    try:
                        save_data()
                        logger.info("character deletion saved successfully")
                    except Exception as e:
                        logger.error(f"failed to save after character deletion: {e}")
                        input("Error saving after character deletion. Please check the logs. Press any key to continue...")
                if user_choice == 5:
                    logger.info("going back to main menu")
                    continue
            elif choice == 2:
                os.system('cls' if os.name == 'nt' else 'clear')
                logger.info("selected inventory management")
                print("Inventory Management")
                options = ["View Inventory", "Remove item", "Move item to storage", "Back"]
                commondefs.print_menu(options)
                user_choice = commondefs.get_user_choice(len(options))
                if user_choice == 1:
                    logger.info("viewing inventory")
                    if not current_inventory:
                        print("Inventory is empty.")
                    else:
                        print("Current Inventory:")
                        for idx, item in enumerate(current_inventory, start=1):
                            print(f"{idx}. {item}")
                    input("Press any key to continue...")
                elif user_choice == 2:
                    logger.info("removing item from inventory")
                    if not current_inventory:
                        print("Inventory is empty.")
                        continue
                    print("Select an item to remove:")
                    for idx, item in enumerate(current_inventory, start=1):
                        print(f"{idx}. {item}")
                    item_choice = commondefs.get_user_choice(len(current_inventory))
                    removed_item = current_inventory.pop(item_choice - 1)
                    print(f"Removed item: {removed_item}")
                    try:
                        save_data()
                        logger.info("item removal saved successfully")
                    except Exception as e:
                        logger.error(f"failed to save after item removal: {e}")
                        input("Error saving after item removal. Please check the logs. Press any key to continue...")
                elif user_choice == 3:
                    logger.info("moving item to storage")
                    if not current_inventory:
                        print("Inventory is empty.")
                        continue
                    print("Select an item to move to storage:")
                    for idx, item in enumerate(current_inventory, start=1):
                        print(f"{idx}. {item}")
                    item_choice = commondefs.get_user_choice(len(current_inventory))
                    moved_item = current_inventory.pop(item_choice - 1)
                    saved_inventories.append(moved_item)
                    print(f"Moved item to storage: {moved_item}")
                    try:
                        save_data()
                        logger.info("item moved to storage saved successfully")
                    except Exception as e:
                        logger.error(f"failed to save after moving item to storage: {e}")
                        input("Error saving after moving item to storage. Please check the logs. Press any key to continue...")
            elif user_choice == 4:
                logger.info("going back to main menu")
                continue
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            sys.exit(1)
    