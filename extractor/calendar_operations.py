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

def add_to_calendar(df, calendars):
    all_calendars = {**calendars, **{'Definite': calendars['Definite']}}
    grouped = df.drop_duplicates(subset=['Event Start Date', 'Account'])

    for index, row in grouped.iterrows():
        event_start_date = pd.Timestamp(row['Event Start Date']).to_pydatetime()
        event_start_time_str = row['Event Start Time 12 Hour']
        event_end_time_str = row['Event End Time 12 Hour']

        event_start_time_dt = pd.Timestamp(event_start_date.strftime('%Y-%m-%d') + ' ' + event_start_time_str).to_pydatetime()
        event_end_time_dt = pd.Timestamp(event_start_date.strftime('%Y-%m-%d') + ' ' + event_end_time_str).to_pydatetime()

        # Convert to UTC
        local_tz = pytz.timezone('America/Chicago')  # Replace with the appropriate local timezone
        event_start_time_utc = local_tz.localize(event_start_time_dt).astimezone(pytz.UTC)
        event_end_time_utc = local_tz.localize(event_end_time_dt).astimezone(pytz.UTC)

        logging.debug(f"Debug: Event Start DateTime in UTC: {event_start_time_utc}")
        logging.debug(f"Debug: Event End DateTime in UTC: {event_end_time_utc}")
        logging.debug(f"Event Start Time in UTC: {event_start_time_utc}")
        logging.debug(f"Event End Time in UTC: {event_end_time_utc}")


        account_name = row['Account']
        event_status = row['Event Status']

        logging.info(f"Trying to add event: {account_name} on {event_start_date}")

        calendar_to_use = calendars.get(event_status)

        if calendar_to_use is None:
            logging.warning(f"Invalid Event Status: {event_status}. Skipping.")
            continue

        should_skip = False
        for cal in all_calendars.values():
            account_name_escaped = account_name.replace("'", "''")
            date_str = event_start_time_utc.strftime('%m/%d/%Y %H:%M %p')
            restriction = f"[Start] = '{date_str}' AND [Subject] = '{account_name_escaped}'"

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
            #appointment.Start = event_start_time_utc  # Use UTC time here
            #appointment.End = event_end_time_utc  # Use UTC time here
                # Explicitly setting the Start and End times in UTC
            appointment.StartUTC = event_start_time_utc
            appointment.EndUTC = event_end_time_utc
            appointment.AllDayEvent = False
            appointment.Save()
            logging.info(f"Successfully added event: {account_name}")
            logging.debug(f"Successfully added event: {account_name} with start time {event_start_time_utc} and end time {event_end_time_utc}")

        except pywintypes.com_error as e:
            logging.error(f"COM error while adding event {account_name}. Error: {e}")
        except Exception as e:
            logging.error(f"Failed to add event {account_name}. Error: {e}")
            logging.debug(f"Failed to add event {account_name}. Error: {e}")

# Function to remove events from a specific calendar
# To remove all events. Modify to update the DataFrame based on the current state of the calendars 
# before running remove_from_calendar(), 
# or by making remove_from_calendar() smart enough to look in all possible calendars 
# regardless of the status in the DataFrame.
def remove_from_calendar(df, calendars, outlook):
    # The rest of your code remains the same

    for index, row in df.drop_duplicates(subset=['Event Start Date', 'Account']).iterrows():
        account_name = row['Account']
        account_name_escaped = account_name.replace("'", "''")
        event_status = row['Event Status']

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