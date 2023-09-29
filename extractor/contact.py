import argparse
import json
import re

# Define the positions and their descriptions
positions = {
    'a1': 'Position A1 Description',
    'a2': 'Position A2 Description',
    'v1': 'Position V1 Description',
    'v2': 'Position V2 Description',
    'l1': 'Position L1 Description',
    'l2': 'Position L2 Description',
    'hand': 'Hand Position Description',
    'crew_chief': 'Crew Chief Description'
}

def is_valid_phone_number(phone):
    # Regular expression pattern to match US phone number format
    pattern = r'^\(\d{3}\) \d{3}-\d{4}$'
    return re.match(pattern, phone) is not None

def gather_contact_info():
    # Initialize an empty list to store contact information
    contacts = []

    while True:
        first_name = input("Enter first name (or 'q' to quit): ")
        if first_name.lower() == 'q':
            break

        last_name = input("Enter last name: ")

        # Initialize phone as an empty string
        phone = ""

        # Flag to control the phone input loop
        valid_phone = False

        while not valid_phone:
            phone = input("Enter phone number (in the format (XXX) XXX-XXXX): ")
            if is_valid_phone_number(phone):
                valid_phone = True
            else:
                print("Invalid phone number format. Please use the format (XXX) XXX-XXXX.")

        # Initialize an empty list to store positions for the current contact
        contact_positions = []

        while True:
            print("Choose position(s) from the following list (enter 'done' to finish):")
            for pos, desc in positions.items():
                print(f"{pos}: {desc}")
            
            position_input = input("Enter a position: ").strip()

            if position_input == 'done':
                break
            
            if position_input in positions:
                contact_positions.append(position_input)
            else:
                print("Invalid position. Please choose from the list.")

        # Get the weight rating
        while True:
            weight = input("Enter weight rating (1, 2, or 3): ")
            if weight in ['1', '2', '3']:
                break
            else:
                print("Invalid weight rating. Please enter 1, 2, or 3.")

        # Create the contact dictionary with the positions list
        contact = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'position': contact_positions,  # Add the positions to the contact
            'weight': int(weight)
        }

        contacts.append(contact)

    return contacts

def save_to_json(contacts, filename='contact.json'):
    with open(filename, 'w') as json_file:
        json.dump(contacts, json_file, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Gather contact information and save it to contact.json.')
    args = parser.parse_args()

    contacts = gather_contact_info()

    if len(contacts) > 0:
        save_to_json(contacts)
        print(f"{len(contacts)} contact(s) saved to contact.json")

if __name__ == '__main__':
    main()
