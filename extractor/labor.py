import os
import json
import win32com.client
from datetime import datetime

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    
    with open(config_path, 'r') as f:
        return json.load(f)

def list_events_by_date(events_calendar, event_date):
    date_start = f"{event_date} 12:00 AM"
    date_end = f"{event_date} 11:59 PM"
    
    restriction = f"[Start] >= '{date_start}' AND [Start] <= '{date_end}'"
    
    appointments = events_calendar.Items
    appointments.Sort("[Start]")
    appointments = appointments.Restrict(restriction)
    
    events = []
    for idx, appointment in enumerate(appointments):
        print(f"{idx + 1}. {appointment.Subject} - {appointment.Start}")
        events.append(appointment)
    
    return events

def generate_messages(selected_event, config):
    event_body = selected_event.Body
    print(f"Event body: {event_body}")

    # Split the event body into lines and remove any trailing carriage returns
    notes = event_body.split('\n')
    notes = [note.rstrip('\r') for note in notes]
    print(f"Notes: {notes}")

    # Extract date_range from the first line of notes
    try:
        date_range = notes[0].split(':')[1].strip()
    except IndexError:
        print("Date range not found in notes.")
        return

    # Extract lead and hand information from notes
    leads_info = notes[1].split(';')[1].strip().split(',')
    hands_info = notes[2].split(';')[1].strip().split(',')
    leads = [lead.strip() for lead in leads_info]
    hands = [hand.strip() for hand in hands_info]
    
    print(f"Leads: {leads}")
    print(f"Hands: {hands}")

    # Generate and print messages for leads
    for lead in leads:
        lead_name = config['leads'].get(lead, lead)  # Use the config name if available, otherwise use the original name
        msg = f"{lead_name}, are you available {date_range}?"
        print(msg)

    # Generate and print messages for hands
    for hand in hands:
        hand_name = config['hands'].get(hand, hand)  # Use the config name if available, otherwise use the original name
        msg = f"{hand_name}, are you available {date_range}?"
        print(msg)


if __name__ == "__main__":
    config = load_config()

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    root_folder = outlook.GetDefaultFolder(9)  # 9 refers to the calendar folder
    
    events_calendar = None
    for folder in root_folder.Folders:
        if folder.Name == 'Definite':
            events_calendar = folder
            break

    if events_calendar:
        event_date = input("Enter the event date (YYYY-MM-DD): ")
        try:
            datetime.strptime(event_date, "%Y-%m-%d")  # Validate date format
            events = list_events_by_date(events_calendar, event_date)
            
            if events:
                choice = int(input("Select an event by entering its number: "))
                selected_event = events[choice - 1]  # Retrieve selected event
                print(f"You selected {selected_event.Subject}")
                
                generate_messages(selected_event, config)
                
            else:
                print("No events found for the given date.")
            
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
    else:
        print("Could not find 'Events' calendar.")
