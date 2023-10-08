import pytz
import datetime
from datetime import datetime
import win32com.client

print("calendar_ops module loaded")

# Get the labor calendar
def get_labor_calendar():
    return get_calendar_by_name("Labor")

def get_calendar_by_name(calendar_name):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    calendar = None

    for folder in outlook.GetDefaultFolder(9).Folders:
        if folder.Name == calendar_name:
            calendar = folder
            break

    return calendar

def create_calendar_event(calendar, subject, start, end, body=""):
    appointment = calendar.Items.Add(1)  # 1 represents olAppointmentItem
    appointment.Subject = subject
    appointment.Start = start
    appointment.End = end
    appointment.Body = body
    appointment.Save()

    return appointment

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

def get_date_from_user(prompt="Which date are you scheduling labor for? (format: YYYY-MM-DD): "):
    while True:
        date_str = input(prompt)
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
