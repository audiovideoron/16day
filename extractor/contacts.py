import json
import re
import os
from gpt4_helper import handle_api_query

# Constants
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
    PATTERN_PHONE = r"\+?(\d\s?){0,14}"
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


def get_position_key(position_name):
    for key, value in POSITIONS.items():
        if value.lower() == position_name.lower():
            return key
    return None


def gather_contact_info(existing_contacts):
    contacts = []
    available_positions = POSITIONS.copy()

    while True:
        first_name = input("Enter first name (or 'q' to quit): ")
        if first_name.lower() == "q":
            break
        last_name = input("Enter last name: ")

        phone = ""
        while True:
            phone = input("Enter phone number (in the format (XXX) XXX-XXXX): ")
            if is_valid_phone_number(phone):
                break
            print("Invalid phone number format. Please use the format (XXX) XXX-XXXX.")

        position_choices = []
        while True:
            if not available_positions:
                print("No more positions available.")
                break

            print(
                "Choose position(s) from the following list (enter 'done' to finish)."
            )
            for pos, desc in available_positions.items():
                print(f"{pos}: {desc}")

            position_input = input(
                "Enter one or multiple positions separated by commas: "
            ).strip()
            if position_input.lower() == "done":
                break

            position_choices_raw = [x.strip() for x in position_input.split(",")]
            position_choices = [get_position_key(pos) for pos in position_choices_raw]

            # Filter out None values if the position is not found
            position_choices = [pos for pos in position_choices if pos]

            if position_choices:
                for pos in position_choices:
                    del available_positions[pos]
                break
            else:
                print("Invalid position(s). Please choose from the list.")

        is_reliable = get_yes_no_input(f"Is {first_name} reliable? (y/n): ")
        is_flexible = get_yes_no_input(f"Is {first_name} flexible? (y/n): ")
        has_client_relations = get_yes_no_input(
            f"Does {first_name} have good rapport with the client? (y/n): "
        )
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
