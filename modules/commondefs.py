version = "1.0.0"
hidden = True

def print_menu(options):
    for i, option in enumerate(options, start=1):
        print(f"[{i}] {option}")