import json
import re
import os

# Constants
POSITIONS = {
    "a1": "a1",
    "a2": "a2",
    "v1": "v1",
    "v2": "v2",
    "l1": "l1",
    "l2": "l2",
    "crew_chief": "crew chief",
    "hand": "hand",
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
    PATTERN_PHONE = r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$"
    return re.match(PATTERN_PHONE, phone) is not None


def get_yes_no_input(prompt):
    return input(prompt).strip().lower() == "y"


def calculate_weight(
    contact_positions, reliable, flexible, client_relations, preferred
):
    weight = sum(POSITION_WEIGHTS[pos] for pos in contact_positions)
    weight += reliable + flexible + client_relations + preferred
    return weight


def generate_unique_id(existing_contacts):
    highest_id = (
        max(int(contact["id"]) for contact in existing_contacts)
        if existing_contacts
        else 0
    )
    return str(highest_id + 1)


def get_position_key(pos):
    for key, value in POSITIONS.items():
        if pos.lower() in value.lower():
            print(f"Found key '{key}' for position '{pos}'")  # Debugging line
            return key
    print(f"Couldn't find a key for position '{pos}'")  # Debugging line

def gather_contact_info(existing_contacts):
    contacts = []

    print("Gathering information for a new contact.")
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    notes = input("Enter notes (optional): ")

    while True:
        phone = input("Enter phone number (in the format (XXX) XXX-XXXX): ")
        if is_valid_phone_number(phone):
            break
        print("Invalid phone number format. Please use the format (XXX) XXX-XXXX.")

    print("Choose position(s) from the following list.")
    for pos, desc in POSITIONS.items():
        print(f"{pos}: {desc}")

    position_input = input("Enter one or multiple positions separated by commas: ").strip()
    position_choices_raw = list(map(str.strip, position_input.split(',')))
    position_choices_input = [get_position_key(pos) for pos in position_choices_raw]
    position_choices = [pos for pos in position_choices_input if pos]

    is_reliable = get_yes_no_input(f"Is {first_name} reliable? (y/n): ")
    is_flexible = get_yes_no_input(f"Is {first_name} flexible? (y/n): ")
    has_client_relations = get_yes_no_input(f"Does {first_name} have good rapport with the client? (y/n): ")
    is_preferred = get_yes_no_input(f"Do you prefer {first_name}? (y/n): ")

    weight = calculate_weight(
        position_choices,
        is_reliable,
        is_flexible,
        has_client_relations,
        is_preferred,
    )

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
        "id": generate_unique_id(existing_contacts),
        "first_name": first_name,
        "last_name": last_name,
        'email': email,
        'notes': notes,
        "phone": phone,
        "position": position_choices,
        "weight": weight,
        "rate": rate,
        "reliable": is_reliable,
        "flexible": is_flexible,
        "client_relations": has_client_relations,
        "preferred": is_preferred,
    }

    contacts.append(contact)
    return contacts


def save_to_json(contacts):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_directory, "contacts.json")

    with open(filename, "w") as json_file:
        json.dump(contacts, json_file, indent=4)


def main():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(current_directory, "contacts.json")

    if os.path.exists(filename):
        with open(filename, "r") as json_file:
            existing_contacts = json.load(json_file)
    else:
        existing_contacts = []

    new_contacts = gather_contact_info(existing_contacts)

    if new_contacts:
        all_contacts = existing_contacts + new_contacts
        save_to_json(all_contacts)
        print(f"{len(new_contacts)} new contact(s) added.")
    else:
        print("No new contacts entered.")


# Your main code
if __name__ == "__main__":
    main()
