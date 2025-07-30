import os
import base64
import json
import logging

version = "1.0.0"
displayname = "Save Decoder"

logger = logging.getLogger(__name__)

saves_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'saves'))
if not os.path.exists(saves_dir):
    logger.info(f"creating saves directory at {saves_dir}")
    os.makedirs(saves_dir)

def decode_save_file(filename):
    logger.info(f"running decode_save_file with filename: {filename}")
    save_path = os.path.join(saves_dir, filename)
    if not filename.endswith('.save'):
        logger.error("input file did not have the .save extension")
        raise ValueError("Input file must have a .save extension.")
    json_filename = filename.replace('.save', '.json')
    py_path = os.path.join(saves_dir, json_filename)
    with open(save_path, "rb") as f:
        encoded = f.read()
    decoded_bytes = base64.b85decode(encoded)
    decoded_str = decoded_bytes.decode("utf-8")
    try:
        data = json.loads(decoded_str)
        pretty_json = json.dumps(data, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"failed to decode JSON from {save_path}: {e}")
        pretty_json = decoded_str

    with open(py_path, "w", encoding="utf-8") as f:
        logger.info(f"writing decoded data to {py_path}")
        f.write(pretty_json)
        logger.info(f"decoded save file written to {py_path}")

    return py_path

def encode_save_file(json_filename):
    logger.info(f"running encode_save_file with filename: {json_filename}")
    py_path = os.path.join(saves_dir, json_filename)
    if not json_filename.endswith('.json'):
        logger.error("input file did not have the .json extension")
        raise ValueError("Input file must have a .json extension.")
    save_filename = json_filename.replace('.json', '.save')
    save_path = os.path.join(saves_dir, save_filename)
    with open(py_path, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        json.loads(content)
    except Exception as e:
        logger.error(f"failed to load JSON from {py_path}: {e}")
        pass
    encoded = base64.b85encode(content.encode("utf-8"))
    with open(save_path, "wb") as f:
        logger.info(f"writing encoded data to {save_path}")
        f.write(encoded)
        logger.info(f"encoded save file written to {save_path}")
    return save_path

def list_save_files():
    return [f for f in os.listdir(saves_dir) if f.endswith('.save')]

def primary():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Available .save files:")
    save_files = list_save_files()
    for idx, fname in enumerate(save_files, 1):
        print(f"{idx}. {fname}")
    print("\nOptions:")
    print("1. Decode a .save file to .json")
    print("2. Encode a .json file to .save")
    choice = input("Enter your choice (1/2): ").strip()
    if choice == "1":
        file_idx = int(input("Enter the number of the .save file to decode: ").strip())
        if 1 <= file_idx <= len(save_files):
            py_path = decode_save_file(save_files[file_idx - 1])
            print(f"Decoded to {py_path}")
        else:
            print("Invalid selection.")
    elif choice == "2":
        py_files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
        print("Available .json files:")
        for idx, fname in enumerate(py_files, 1):
            print(f"{idx}. {fname}")
        file_idx = int(input("Enter the number of the .json file to encode: ").strip())
        if 1 <= file_idx <= len(py_files):
            save_path = encode_save_file(py_files[file_idx - 1])
            print(f"Encoded to {save_path}")
        else:
            print("Invalid selection.")
    else:
        print("Invalid choice.")
