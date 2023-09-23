import logging
import pywintypes
import pandas as pd
import win32com.client

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
    grouped = df.drop_duplicates(subset=['Event Start Date', 'Account'])
    for index, row in grouped.iterrows():
        event_start_date = pd.Timestamp(row['Event Start Date']).to_pydatetime()
        account_name = row['Account']
        event_status = row['Event Status']

        logging.info(f"Trying to add event: {account_name} on {event_start_date}")

        calendar_to_use = calendars.get(event_status)
        
        if calendar_to_use is None:
            logging.warning(f"Invalid Event Status: {event_status}. Skipping.")
            continue

        # Add this code here to escape the account_name and format the date.
        account_name_escaped = account_name.replace("'", "''")
        date_str = event_start_date.strftime('%m/%d/%Y %H:%M %p')
        restriction = f"[Start] = '{date_str}' AND [Subject] = '{account_name_escaped}'"

        existing_appointments = calendar_to_use.Items.Restrict(restriction)
        
        if existing_appointments.Count == 0:
            try:
                appointment = calendar_to_use.Items.Add(1)
                appointment.Subject = account_name
                appointment.Start = event_start_date
                appointment.AllDayEvent = True
                appointment.Save()
                logging.info(f"Successfully added event: {account_name}")
            except pywintypes.com_error as e:
                logging.error(f"COM error while adding event {account_name}. Error: {e}")
            except Exception as e:
                logging.error(f"Failed to add event {account_name}. Error: {e}")

                logging.error(f"Failed to add event {account_name}. Error: {e}")
    pass

# Function to remove events from a specific calendar
def remove_from_calendar(df, calendars):
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
    pass

# Future function to move events between calendars
def move_to_calendar(df, from_calendar, to_calendar):
    # Implementation yet to be done
    pass
