import datetime
import pytz
from win32com.client import Dispatch
from twilio.rest import Client
from datetime import datetime, timedelta
from calendar_ops import (
    get_calendar_by_name,
    create_calendar_event,
    get_definite_calendar,
    get_outlook_events_for_date,
    get_labor_calendar,
)
from labor_ops import (
    gather_labor_requirements,
    schedule_labor_for_event,
    generate_labor_event_details,
    get_labor_positions_and_counts,
    get_labor_times_for_days,
    generate_labor_days_list,
    select_labor_days,
    get_labor_times_for_day,
)

def main():
    labor_calendar = get_labor_calendar()
    if not labor_calendar:
        print("Unable to access the 'Labor' calendar in Outlook.")
        return

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

    if len(events) == 1:
        print(f"\nThe only event on {target_date_str} is '{events[0].Subject}'.")
        selected_event = events[0]
    else:
        # Display the events and let the user choose one
        print("\nAvailable events on " + target_date_str + ":")
        for idx, event in enumerate(events, 1):
            # Use date() method on the datetime object to display only the date
            start_date = event.Start.astimezone(pytz.timezone("America/Chicago")).date()
            end_date = event.End.astimezone(pytz.timezone("America/Chicago")).date()
            print(f"{idx}. {event.Subject} ({start_date} - {end_date})")

        # User specifies which event they're interested in
        event_choice = int(input("Which event are you scheduling labor for? "))
        selected_event = events[event_choice - 1]

    # Schedule labor for the chosen event
    schedule_labor_for_event(selected_event)

if __name__ == "__main__":
    main()
