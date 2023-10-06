import json
import datetime
import win32com.client
import pytz
from win32com.client import Dispatch
from twilio.rest import Client

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
            return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
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
        datetime.datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0)
    )
    end_time_local = local_tz.localize(
        datetime.datetime(
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

        # Get the start time
        start_time = input("What is the start time for the labor shift? (format: HH:MM AM/PM): ")
        
        # Convert the input into a datetime object
        start_datetime = datetime.strptime(f"{day.strftime('%Y-%m-%d')} {start_time}", '%Y-%m-%d %I:%M %p')
        
        # Get the end time
        end_time = input("What is the end time for the labor shift? (format: HH:MM AM/PM): ")

        # Convert the input into a datetime object
        end_datetime = datetime.strptime(f"{day.strftime('%Y-%m-%d')} {end_time}", '%Y-%m-%d %I:%M %p')

        labor_schedule[day] = {
            "start_time": start_datetime,
            "end_time": end_datetime
        }

    return labor_schedule


def schedule_labor_for_event(event):
    # Extract the event details
    event_name = event.Subject
    event_start_date = event.Start.date()
    event_end_date = event.End.date()

    # Prompt user for the labor scheduling window
    print(
        f"\nThe actual event '{event_name}' starts on {event_start_date} and ends on {event_end_date}."
    )
    labor_start_date_input = input(
        "When do you want to start scheduling labor? (format: YYYY-MM-DD): "
    )
    labor_end_date_input = input(
        "Until when do you want to schedule labor? (format: YYYY-MM-DD): "
    )

    # Convert inputs to dates
    labor_start_date = datetime.datetime.strptime(
        labor_start_date_input, "%Y-%m-%d"
    ).date()
    labor_end_date = datetime.datetime.strptime(labor_end_date_input, "%Y-%m-%d").date()

    # List the available dates for labor scheduling
    delta = labor_end_date - labor_start_date
    available_dates = [
        labor_start_date + datetime.timedelta(days=i) for i in range(delta.days + 1)
    ]

    print(f"\nFor the event '{event_name}', on which specific days do you need labor?")
    for index, date in enumerate(available_dates, 1):
        # Indicate if the date is outside the event window
        indication = ""
        if date < event_start_date or date > event_end_date:
            indication = "(Outside event window)"

        print(f"{index}. {date.strftime('%Y-%m-%d')} {indication}")

    # Here, you can continue with additional steps, e.g., labor time selection, position selection, etc.


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
    target_date = datetime.datetime.strptime(target_date_str, "%Y-%m-%d")

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
