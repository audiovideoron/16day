import logging
import pywintypes
import pandas as pd
import win32com.client
import pytz


# Common function to set up the Outlook application and get the calendars
def setup_outlook_calendars(folder_names):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    root_folder = outlook.GetDefaultFolder(9)
    calendars = {}

    for folder in root_folder.Folders:
        if folder.Name in folder_names:
            calendars[folder.Name] = folder

    return calendars


# Function to add events to a specific calendar
def add_to_calendar_with_earliest_start_end(df, calendars):
    unique_events = {}

    for _, row in df.iterrows():
        event_start_date = pd.Timestamp(row["Event Start Date"]).to_pydatetime()
        account_name = row["Account"]
        event_status = row.get("Event Status", "Definite")

        # Create a unique identifier for each event based on Account and Event Start Date
        event_identifier = (account_name, event_start_date)

        if event_identifier not in unique_events:
            unique_events[event_identifier] = {
                "start_time": None,
                "end_time": None,
                "account_name": account_name,
                "event_status": event_status,
            }

        start_time = pd.Timestamp(
            event_start_date.strftime("%Y-%m-%d")
            + " "
            + row["Event Start Time 12 Hour"]
        )
        end_time = pd.Timestamp(
            event_start_date.strftime("%Y-%m-%d") + " " + row["Event End Time 12 Hour"]
        )

        if (
            unique_events[event_identifier]["start_time"] is None
            or start_time < unique_events[event_identifier]["start_time"]
        ):
            unique_events[event_identifier]["start_time"] = start_time

        if (
            unique_events[event_identifier]["end_time"] is None
            or end_time > unique_events[event_identifier]["end_time"]
        ):
            unique_events[event_identifier]["end_time"] = end_time

    for event_identifier, event_data in unique_events.items():
        event_start_time = event_data["start_time"]
        event_end_time = event_data["end_time"]
        account_name = event_data["account_name"]
        event_status = event_data["event_status"]

        # Convert to UTC
        local_tz = pytz.timezone(
            "America/Chicago"
        )  # Replace with the appropriate local timezone
        event_start_time_utc = local_tz.localize(event_start_time).astimezone(pytz.UTC)
        event_end_time_utc = local_tz.localize(event_end_time).astimezone(pytz.UTC)

        # Log and add the event to the calendar
        logging.debug(f"Debug: Event Start DateTime in UTC: {event_start_time_utc}")
        logging.debug(f"Debug: Event End DateTime in UTC: {event_end_time_utc}")
        logging.debug(f"Event Start Time in UTC: {event_start_time_utc}")
        logging.debug(f"Event End Time in UTC: {event_end_time_utc}")
        logging.info(
            f"Trying to add event: {account_name} on {event_start_time.date()}"
        )

        calendar_to_use = calendars.get(event_status)

        if calendar_to_use is None:
            logging.warning(f"Invalid Event Status: {event_status}. Skipping.")
            continue

        should_skip = False
        for cal in calendars.values():
            account_name_escaped = account_name.replace("'", "''")
            date_str = event_start_time_utc.strftime("%m/%d/%Y %H:%M %p")
            restriction = (
                f"[Start] = '{date_str}' AND [Subject] = '{account_name_escaped}'"
            )

            existing_appointments = cal.Items.Restrict(restriction)

            if existing_appointments.Count > 0:
                logging.info(f"Event already exists in a calendar. Skipping.")
                should_skip = True
                break

        if should_skip:
            continue

        logging.debug(f"About to Add Event: {account_name}")
        logging.debug(f"With Start Time: {event_start_time_utc}")
        logging.debug(f"And End Time: {event_end_time_utc}")

        try:
            appointment = calendar_to_use.Items.Add(1)
            appointment.Subject = account_name
            appointment.StartUTC = event_start_time_utc
            appointment.EndUTC = event_end_time_utc
            appointment.AllDayEvent = False
            appointment.Save()
            logging.info(f"Successfully added event: {account_name}")
            logging.debug(
                f"Successfully added event: {account_name} with start time {event_start_time_utc} and end time {event_end_time_utc}"
            )

        except pywintypes.com_error as e:
            logging.error(f"COM error while adding event {account_name}. Error: {e}")
        except Exception as e:
            logging.error(f"Failed to add event {account_name}. Error: {e}")
            logging.debug(f"Failed to add event {account_name}. Error: {e}")


# Function to remove events from a specific calendar
def remove_from_calendar(df, calendars, outlook):
    # The rest of your code remains the same

    for index, row in df.drop_duplicates(
        subset=["Event Start Date", "Account"]
    ).iterrows():
        account_name = row["Account"]
        account_name_escaped = account_name.replace("'", "''")
        event_status = row["Event Status"]

        logging.info(f"Trying to remove event: {account_name}")

        calendar_to_use = calendars.get(event_status)

        if calendar_to_use is None:
            logging.warning(f"Invalid Event Status: {event_status}. Skipping.")
            continue

        try:
            restriction = f"[Subject] = '{account_name_escaped}'"
            logging.info(f"Applying restriction: {restriction}")
            filtered_appointments = calendar_to_use.Items.Restrict(restriction)
            for appointment in filtered_appointments:
                appointment.Delete()
            logging.info(f"Successfully removed event: {account_name}")
        except Exception as e:
            logging.error(f"Failed to remove event {account_name}. Error: {e}")
