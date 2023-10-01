import argparse
import json
import re

def is_valid_phone_number(phone):
    pattern = r"^\(\d{3}\) \d{3}-\d{4}$"
    return re.match(pattern, phone) is not None

positions_dict = {
    "a1": 2,
    "a2": 1,
    "v1": 2,
    "v2": 1,
    "l1": 2,
    "l2": 1,
    "crew_chief": 2,
    "hand": 1,
}

def calculate_weight(contact_positions, reliable, flexible, client_relations, preferred):
    weight = sum(positions_dict[pos] for pos in contact_positions)
    if reliable:
        weight += 1
    if flexible:
        weight += 1
    if client_relations:
        weight += 1
    if preferred:
        weight += 1
    return weight

def gather_contact_info():
    contacts = []
    positions = {
        "a1": "Audio Level 1",
        "a2": "Audio Level 2",
        "v1": "Video Level 1",
        "v2": "Video Level 2",
        "l1": "Lighting Level 1",
        "l2": "Lighting Level 2",
        "crew_chief": "Crew Chief",
        "hand": "Hand",
    }

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
            else:
                print("Invalid phone number format. Please use the format (XXX) XXX-XXXX.")

        contact_positions = []
        available_positions = positions.copy()
        while True:
            if not available_positions:
                print("No more positions available.")
                break

            print("Choose position(s) from the following list (enter 'done' to finish):")
            for pos, desc in available_positions.items():
                print(f"{pos}: {desc}")

            position_input = input("Enter a position: ").strip()
            if position_input == 'done':
                break

            if position_input in available_positions:
                contact_positions.append(position_input)

                if position_input in ["a1", "v1", "l1"]:
                    corresponding_position = position_input[0] + "2"
                    del available_positions[corresponding_position]

                del available_positions[position_input]
            else:
                print("Invalid position. Please choose from the list.")

        is_reliable = input(f"Is {first_name} reliable? (y/n): ").strip().lower() == 'y'
        is_flexible = input(f"Is {first_name} flexible? (y/n): ").strip().lower() == 'y'
        has_client_relations = input(f"Does {first_name} have good rapport with the client? (y/n): ").strip().lower() == 'y'
        is_preferred = input(f"Do you prefer {first_name}? (y/n): ").strip().lower() == 'y'

        weight = calculate_weight(contact_positions, is_reliable, is_flexible, has_client_relations, is_preferred)

        rate = 0.0
        while True:
            rate = input("Enter rate: ")
            try:
                rate = float(rate)
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
    parser = argparse.ArgumentParser(description="Gather contact info and save to contact.json.")
    args = parser.parse_args()

    try:
        with open("contact.json", "r") as json_file:
            existing_contacts = json.load(json_file)
    except FileNotFoundError:
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
