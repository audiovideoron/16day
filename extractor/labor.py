import json
import datetime
import win32com.client
import pytz
from win32com.client import Dispatch
from twilio.rest import Client
from datetime import datetime, timedelta


# Constants
LABOR_JSON_PATH = "labor.json"
AVAILABILITY_JSON_PATH = "availability.json"
LABOR_COST_PER_HOUR = 110

# Initialize Twilio client (Make sure to replace with your own credentials)
TWILIO_ACCOUNT_SID = "YOUR_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_AUTH_TOKEN"
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Helper Functions


def get_definite_calendar():
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    calendar_folder = outlook.GetDefaultFolder(9)  # 9 refers to the calendar folder

    # Check if the main Calendar is named "Definite"
    if calendar_folder.Name == "Definite":
        return calendar_folder

    # Otherwise, loop through subfolders to find "Definite"
    for subfolder in calendar_folder.Folders:
        if subfolder.Name == "Definite":
            return subfolder

    return None  # If "Definite" calendar is not found


definite_calendar = get_definite_calendar()
if definite_calendar:
    print("Definite calendar found!")
else:
    print("Definite calendar not found!")


def get_date_from_user():
    while True:
        date_str = input(
            "Which date are you scheduling labor for? (format: YYYY-MM-DD): "
        )
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please try again.")


def get_outlook_events_for_date(target_date):
    """Fetches events from the 'Definite' Outlook calendar for the given date."""
    calendar = get_definite_calendar()
    if not calendar:
        print("Unable to access the 'Definite' calendar in Outlook.")
        return []

    # Convert target_date to the 'America/Chicago' timezone and get the start and end times
    local_tz = pytz.timezone("America/Chicago")
    start_time_local = local_tz.localize(
        datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    )
    end_time_local = local_tz.localize(
        datetime(
            target_date.year, target_date.month, target_date.day, 23, 59, 59
        )
    )

    # Convert start and end times to UTC
    start_time_utc = start_time_local.astimezone(pytz.UTC)
    end_time_utc = end_time_local.astimezone(pytz.UTC)

    # Manually filter events
    events_on_date = []
    for event in calendar.Items:
        if event.Start <= end_time_utc and event.End >= start_time_utc:
            events_on_date.append(event)

    return events_on_date

def get_labor_positions_and_counts():
    # Predefined list of labor positions
    labor_positions = ["Technician", "Audio Engineer", "Stage Manager", "Other"]
    
    selected_positions = {}
    print("\nAvailable labor positions:")
    for index, position in enumerate(labor_positions, 1):
        print(f"{index}. {position}")

    positions_input = input("Select the positions you need (comma separated, e.g. 1,2,3 or type 'Other'): ").split(',')
    
    for pos in positions_input:
        if pos.strip().isdigit():
            index = int(pos.strip()) - 1
            if 0 <= index < len(labor_positions):
                position_name = labor_positions[index]
                if position_name == "Other":
                    position_name = input("Please specify the labor position: ").strip()
                count = int(input(f"How many {position_name}s do you need? "))
                selected_positions[position_name] = count

    return selected_positions

# Later in the `schedule_labor_for_event` function, after getting the labor times:
labor_requirements = get_labor_positions_and_counts()
print("\nLabor Requirements:")
for position, count in labor_requirements.items():
    print(f"{position}: {count}")


def filter_and_rank_workers(skillset=None):
    with open(LABOR_JSON_PATH, "r") as file:
        workers = json.load(file)
    # Assuming each worker has a 'weight' key and an optional 'skillset' key.
    if skillset:
        workers = [w for w in workers if w["skillset"] == skillset]
    return sorted(workers, key=lambda x: x["weight"], reverse=True)


def send_sms_notification(worker, message):
    twilio_client.messages.create(
        body=message,
        from_="+1234567890",  # Your Twilio number
        to=worker["phone_number"],
    )


# Primary Logic Functions
def select_event_for_date(target_date):
    events = get_outlook_events_for_date(target_date)

    if not events:
        print(f"No events found for {target_date}.")
        return None

    print("\nEvents for the selected date:")
    for idx, event in enumerate(events, 1):
        print(f"{idx}. {event.Subject} ({event.Start} - {event.End})")

    while True:
        choice = input(f"Select an event (1-{len(events)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(events):
            return events[int(choice) - 1]
        else:
            print("Invalid choice. Please select a valid event number.")

def get_labor_times_for_days(days):
    labor_schedule = {}
    for day in days:
        print(f"\nFor {day.strftime('%Y-%m-%d')}:")

        start_time_str = input("What is the start time for the labor shift? (format: HH:MM AM/PM): ")
        start_time = datetime.strptime(start_time_str, '%I:%M %p').time()

        end_time_str = input("What is the end time for the labor shift? (format: HH:MM AM/PM): ")
        end_time = datetime.strptime(end_time_str, '%I:%M %p').time()

        labor_schedule[day] = {
            'start_time': start_time,
            'end_time': end_time
        }

    return labor_schedule

def generate_labor_days_list(event_start, event_end, labor_start, labor_end):
    """
    Generate a list of dates for labor scheduling. This includes the days of the event and any additional days 
    specified by the user for labor scheduling before or after the event.
    """
    # Create a list of days based on the start and end dates of the event
    event_days = [event_start + timedelta(days=x) for x in range(0, (event_end-event_start).days + 1)]
    
    # Extend the list to include additional days specified by the user for labor scheduling
    labor_days = [labor_start + timedelta(days=x) for x in range(0, (labor_end-labor_start).days + 1)]
    
    # Combine the two lists and remove duplicates
    all_days = list(set(event_days + labor_days))
    
    # Sort the combined list
    all_days.sort()
    
    return all_days


def select_labor_days(days, event_start_date, event_end_date):
    """Let the user select specific days they want to schedule labor."""
    print("\nFor the event, on which specific days do you need labor?")
    for idx, day in enumerate(days, 1):
        status = "(Event day)" if event_start_date.date() <= day <= event_end_date.date() else "(Outside event window)"
        print(f"{idx}. {day} {status}")

    selected_indices = input("Please select days for which you want to schedule labor (comma separated, e.g. 1,2,3): ").split(',')
    selected_days = [days[int(idx) - 1] for idx in selected_indices]

    return selected_days

def get_labor_times_for_day(day):
    """Get the start and end times for labor on a specific day."""
    start_time_str = input(f"\nFor {day}:\nWhat is the start time for the labor shift? (format: HH:MM AM/PM): ")
    end_time_str = input("What is the end time for the labor shift? (format: HH:MM AM/PM): ")

    start_time = datetime.strptime(start_time_str, '%I:%M %p').time()
    end_time = datetime.strptime(end_time_str, '%I:%M %p').time()

    return start_time, end_time


def schedule_labor_for_event(event):
    event_name = event.Subject
    event_start = event.Start
    event_end = event.End

    print(f"\nThe actual event '{event_name}' starts on {event_start.date()} and ends on {event_end.date()}.")

    while True:
        # Ask the user for labor scheduling outside of the event's start and end times
        labor_start_date = datetime.strptime(input("When do you want to start scheduling labor? (format: YYYY-MM-DD): "), '%Y-%m-%d').date()
        labor_end_date = datetime.strptime(input("Until when do you want to schedule labor? (format: YYYY-MM-DD): "), '%Y-%m-%d').date()

        days_for_labor = generate_labor_days_list(event_start.date(), event_end.date(), labor_start_date, labor_end_date)
        selected_labor_days = select_labor_days(days_for_labor, event_start, event_end)

        for day in selected_labor_days:
            get_labor_times_for_day(day)

        # Ask if user wants to schedule more labor
        another_shift = input("Would you like to schedule another shift for a different position or day for the same event? (Yes/No): ").lower()
        if another_shift == "no":
            print("\nLabor scheduling for the selected event is complete.")
            break

        # If the answer isn't 'yes' or 'no', keep asking
        elif another_shift != "yes":
            print("Invalid input. Please answer with 'Yes' or 'No'.")


def main():
    # Fetch the 'Definite' calendar
    calendar = get_definite_calendar()
    if not calendar:
        print("Unable to access the 'Definite' calendar in Outlook.")
        return

    # Ask the user for the target date
    target_date_str = input(
        "Which date are you scheduling labor for? (format: YYYY-MM-DD): "
    )
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d")

    # Fetch and display events from the calendar for that date
    events = get_outlook_events_for_date(target_date)
    if not events:
        print(f"No events found for {target_date_str}.")
        return

    # Display the events and let the user choose one
    print("\nEvents for the selected date:")
    for idx, event in enumerate(events, 1):
        start = event.Start.astimezone(pytz.timezone("America/Chicago"))
        end = event.End.astimezone(pytz.timezone("America/Chicago"))
        print(f"{idx}. {event.Subject} ({start} - {end})")

    # User specifies which event they're interested in
    event_choice = int(input("Which event are you scheduling labor for? "))
    selected_event = events[event_choice - 1]

    # Schedule labor for the chosen event
    schedule_labor_for_event(selected_event)


if __name__ == "__main__":
    main()
