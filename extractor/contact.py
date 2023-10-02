import json
import re
from json.decoder import JSONDecodeError

# Constants
PATTERN_PHONE = r"^\(\d{3}\) \d{3}-\d{4}$"
POSITIONS = {
    "a1": "Audio Level 1",
    "a2": "Audio Level 2",
    "v1": "Video Level 1",
    "v2": "Video Level 2",
    "l1": "Lighting Level 1",
    "l2": "Lighting Level 2",
    "crew_chief": "Crew Chief",
    "hand": "Hand",
}
POSITION_WEIGHTS = {
    "a1": 2,
    "a2": 1,
    "v1": 2,
    "v2": 1,
    "l1": 2,
    "l2": 1,
    "crew_chief": 2,
    "hand": 1,
}

def is_valid_phone_number(phone):
    patterns = [
        r"^\(\d{3}\) \d{3}-\d{4}$",  # (XXX) XXX-XXXX
        r"^\d{3}-\d{3}-\d{4}$",      # XXX-XXX-XXXX
        r"^\d{10}$",                 # XXXXXXXXXX
        # Add more patterns as needed
    ]

    return any(re.match(pattern, phone) for pattern in patterns)

def get_yes_no_input(prompt):
    return input(prompt).strip().lower() == 'y'

def calculate_weight(contact_positions, reliable, flexible, client_relations, preferred):
    weight = sum(POSITION_WEIGHTS[pos] for pos in contact_positions)
    weight += reliable + flexible + client_relations + preferred
    return weight

def gather_contact_info():
    contacts = []
    available_positions = POSITIONS.copy()
    
    while True:
        first_name = input("Enter first name (or 'q' to quit): ")
        if first_name.lower() == 'q':
            break
        last_name = input("Enter last name: ")

        phone = ''
        while True:
            phone = input("Enter phone number (in the format (XXX) XXX-XXXX): ")
            if is_valid_phone_number(phone):
                break
            print("Invalid phone number format. Please use the format (XXX) XXX-XXXX.")

        contact_positions = []
        while True:
            if not available_positions:
                print("No more positions available.")
                break
            print("Choose position(s) from the following list (enter 'done' to finish).")
            for pos, desc in available_positions.items():
                print(f"{pos}: {desc}")

            position_input = input("Enter one or multiple positions separated by commas: ").strip().replace(" ", "")
            if position_input == 'done':
                break
            selected_positions = position_input.split(',')
            valid_positions = all(pos in available_positions for pos in selected_positions)
            if valid_positions:
                contact_positions.extend(selected_positions)
                for pos in selected_positions:
                    del available_positions[pos]
            else:
                print("Invalid position(s). Please choose from the list.")

        is_reliable = get_yes_no_input(f"Is {first_name} reliable? (y/n): ")
        is_flexible = get_yes_no_input(f"Is {first_name} flexible? (y/n): ")
        has_client_relations = get_yes_no_input(f"Does {first_name} have good rapport with the client? (y/n): ")
        is_preferred = get_yes_no_input(f"Do you prefer {first_name}? (y/n): ")

        weight = calculate_weight(contact_positions, is_reliable, is_flexible, has_client_relations, is_preferred)

        rate = 0.0
        while True:
            rate_input = input("Enter rate: ")
            try:
                rate = float(rate_input)
                if rate < 0:
                    print("Rate must be positive. Try again.")
                else:
                    break
            except ValueError:
                print("Invalid rate. Please enter a numeric rate.")

        contact = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'position': contact_positions,
            'weight': weight,
            'rate': rate,
            'reliable': is_reliable,
            'flexible': is_flexible,
            'client_relations': has_client_relations,
            'preferred': is_preferred
        }
        contacts.append(contact)
    return contacts

def save_to_json(contacts, filename="contact.json"):
    with open(filename, "w") as json_file:
        json.dump(contacts, json_file, indent=4)

def main():
    try:
        with open("contact.json", "r") as json_file:
            existing_contacts = json.load(json_file)
    except (FileNotFoundError, JSONDecodeError):
        existing_contacts = []

    new_contacts = gather_contact_info()

    if new_contacts:
        all_contacts = existing_contacts + new_contacts
        save_to_json(all_contacts)
        print(f"{len(new_contacts)} new contact(s) added.")
    else:
        print("No new contacts entered.")

if __name__ == "__main__":
    main()
