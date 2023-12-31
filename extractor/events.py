import os
import json
import pandas as pd
import win32com.client
import logging
from calendar_operations import add_to_calendar_with_earliest_start_end, remove_from_calendar

# Configure the logging system
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    logging.info("Starting main application.")

    try:
        config = load_config()
    except FileNotFoundError as e:
        logging.error("Config file not found!")
        exit(1)
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON config!")
        exit(1)

    xlsx_file = config.get("excel_file", "./16DayOct.xlsx")
    try:
        df = pd.read_excel(xlsx_file)
    except FileNotFoundError as e:
        logging.error(f"Excel file {xlsx_file} not found!")
        exit(1)

    # Log DataFrame details
    logging.debug(f"Shape of the DataFrame before filters: {df.shape}")
    logging.debug(f"Data types in the DataFrame before filters: {df.dtypes}")

    print("Debug: Head of DataFrame after reading Excel:")
    print(df.head())
    logging.debug(f"DataFrame Head: {df.head()}")

    logging.info("Applying filters.")
    df = df[~df["Function Room"].isin(config["exclude_function_room"])]
    df = df[~df["Event Type"].isin(config["exclude_event_type"])]
    df = df[df["Event Type"].isin(config["include_event_type"])]

    # Log DataFrame details after filters
    logging.debug(f"Shape of the DataFrame after filters: {df.shape}")
    logging.debug(f"Data types in the DataFrame after filters: {df.dtypes}")

    # Initialize the Outlook object
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    root_folder = outlook.GetDefaultFolder(9)

    # Initialize the specific calendars
    calendars = {}
    for folder in root_folder.Folders:
        if folder.Name in ["Definite", "Tentative", "Prospect"]:
            calendars[folder.Name] = folder

    if not calendars:
        logging.error("Could not find required calendars.")
        exit(1)

    action = (
        input("Would you like to 'Add' or 'Remove' events? (Enter 'Add' or 'Remove'): ")
        .strip()
        .lower()
    )

    if action == "add":
        logging.info("Adding events to calendars.")
        add_to_calendar_with_earliest_start_end(df, calendars)
    elif action == "remove":
        logging.info("Removing events from calendars.")
        remove_from_calendar(df, calendars, outlook)
    else:
        logging.error("Invalid action choice.")
        print("Invalid choice. Please enter 'Add' or 'Remove'.")
