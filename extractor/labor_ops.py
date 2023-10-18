import json
import datetime
import pytz
from datetime import datetime, timedelta
from twilio.rest import Client
from calendar_ops import get_date_from_user, get_labor_calendar, create_calendar_event


# Constants
LABOR_JSON_PATH = "labor.json"
AVAILABILITY_JSON_PATH = "availability.json"
LABOR_COST_PER_HOUR = 110

# Initialize Twilio client (Make sure to replace with your own credentials)
TWILIO_ACCOUNT_SID = "YOUR_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_AUTH_TOKEN"
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def gather_labor_requirements():
    pass


def generate_labor_event_details():
    pass


def get_labor_positions_and_counts():
    labor_positions = ["Technician", "Audio Engineer", "Stage Manager", "Other"]
    selected_positions = {}

    print("\nAvailable labor positions:")
    for index, position in enumerate(labor_positions, 1):
        print(f"{index}. {position}")

    while True:
        positions_input = input(
            "Select the positions you need (comma separated, e.g. 1,2,3,4): "
        ).split(",")

        if all(pos.strip().isdigit() for pos in positions_input):
            break
        else:
            print("Invalid input. Please enter numbers corresponding to the positions.")

    for pos in positions_input:
        pos = pos.strip()
        index = int(pos) - 1

        if 0 <= index < len(labor_positions):
            position_name = labor_positions[index]

            if position_name == "Other":
                position_name = input("Please specify the labor position: ").strip()

            while True:
                count_input = input(f"How many {position_name}s do you need? ")
                if count_input.isdigit() and int(count_input) >= 0:
                    selected_positions[position_name] = int(count_input)
                    break
                else:
                    print("Invalid count. Please enter a non-negative integer.")
        else:
            print(f"Invalid index {index + 1}. Skipping.")

    return selected_positions



def get_labor_times_for_days(days):
    labor_schedule = {}
    for day in days:
        print(f"\nFor {day.strftime('%Y-%m-%d')}:")

        start_time_str = input("What is the start time? (format: HH:MM AM/PM): ")
        start_time = datetime.strptime(start_time_str, "%I:%M %p").time()

        end_time_str = input("What is the end time? (format: HH:MM AM/PM): ")
        end_time = datetime.strptime(end_time_str, "%I:%M %p").time()

        labor_schedule[day] = {"start_time": start_time, "end_time": end_time}

    return labor_schedule


def generate_labor_days_list(event_start, event_end, labor_start, labor_end):
    """
    Generate a list of dates for labor scheduling. This includes the days of the event and any additional days
    specified by the user for labor scheduling before or after the event.
    """
    # Create a list of days based on the start and end dates of the event
    event_days = [
        event_start + timedelta(days=x)
        for x in range(0, (event_end - event_start).days + 1)
    ]

    # Extend the list to include additional days specified by the user for labor scheduling
    labor_days = [
        labor_start + timedelta(days=x)
        for x in range(0, (labor_end - labor_start).days + 1)
    ]

    # Combine the two lists and remove duplicates
    all_days = list(set(event_days + labor_days))

    # Sort the combined list
    all_days.sort()

    return all_days


def select_labor_days(days, event_start_date, event_end_date):
    """Let the user select specific days they want to schedule labor."""

    if len(days) == 1:  # If there's only one day, return it without asking the user
        return days

    print("\nSelect specific days for labor:")
    for idx, day in enumerate(days, 1):
        status = (
            "(Event day)"
            if event_start_date <= day <= event_end_date
            else "(Outside event window)"
        )
        print(f"{idx}. {day} {status}")

    selected_indices = input(
        "Please select days for which you want to schedule labor (comma separated, e.g. 1,2,3): "
    ).split(",")
    selected_days = [days[int(idx) - 1] for idx in selected_indices]

    return selected_days


def get_labor_times_for_day(day):
    """Get the start and end times for labor on a specific day."""
    local_tz = pytz.timezone("America/Chicago")

    start_time_str = input(
        f"\nFor {day}:\nLabor shift start time: (format: HH:MM AM/PM): "
    )
    end_time_str = input("Labor shift end time: (format: HH:MM AM/PM): ")

    # Convert the time strings to datetime.time objects
    start_time_dt = datetime.strptime(start_time_str, "%I:%M %p") - timedelta(hours=5)
    end_time_dt = datetime.strptime(end_time_str, "%I:%M %p") - timedelta(hours=5)

    # Use .time() to extract only the time component
    start_time = start_time_dt.time()
    end_time = end_time_dt.time()

    # Combine day (which is a date) with start_time and end_time to create timezone-aware datetime objects
    start_datetime = local_tz.localize(datetime.combine(day, start_time))
    end_datetime = local_tz.localize(datetime.combine(day, end_time))

    return start_datetime, end_datetime


def schedule_labor_for_event(selected_event):
    # Displaying selected event details
    event_start = selected_event.Start.astimezone(
        pytz.timezone("America/Chicago")
    ).date()
    event_end = selected_event.End.astimezone(pytz.timezone("America/Chicago")).date()

    # Getting labor start and end dates
    labor_start_date = get_date_from_user(
        "Start labor date range: (format: YYYY-MM-DD): "
    )
    labor_end_date = get_date_from_user("End labor date range: (format: YYYY-MM-DD): ")

    # Generate a list of days for which labor needs to be scheduled
    days_for_labor = generate_labor_days_list(
        labor_start_date, labor_end_date, event_start, event_end
    )

    # Selecting specific days for labor
    selected_labor_days = select_labor_days(days_for_labor, event_start, event_end)

    # Gather labor positions and counts
    labor_requirements = get_labor_positions_and_counts()
    print("\nLabor Requirements:")
    for position, count in labor_requirements.items():
        print(f"{position}: {count}")

    # Construct the labor_schedule dictionary
    labor_schedule = {}
    for day in selected_labor_days:
        start_datetime, end_datetime = get_labor_times_for_day(day)
        labor_schedule[day] = {
            "start_time": start_datetime.time(),
            "end_time": end_datetime.time(),
            "positions": labor_requirements,
        }

    # Create labor events in the 'Labor' calendar for each day
    local_tz = pytz.timezone("America/Chicago")
    labor_calendar = get_labor_calendar()

    for day, details in labor_schedule.items():
        # Construct the event_body for each day
        event_body = "Available labor positions:\n"
        for position, count in details["positions"].items():
            event_body += f"{position}: {count}\n"

        # Construct the event_subject for each day
        event_subject = ", ".join(
            [
                f"{count} x {position}"
                for position, count in details["positions"].items()
            ]
        )

        # Use already localized datetime
        event_start = local_tz.localize(datetime.combine(day, details["start_time"]))
        event_end = local_tz.localize(datetime.combine(day, details["end_time"]))

        create_calendar_event(
            labor_calendar, event_subject, event_start, event_end, event_body
        )

    # Ask if the user wants to schedule another shift
    another_shift = (
        input(
            "Would you like to schedule another shift for a different position or day for the same event? (Yes/No): "
        )
        .strip()
        .lower()
    )

    if another_shift == "yes":
        # Recursively call the same function to schedule another shift
        schedule_labor_for_event(selected_event)
    else:
        print("\nLabor scheduling for the selected event is complete.")


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
