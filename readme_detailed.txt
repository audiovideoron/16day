### **Introduction**

- Contact: Ron Parker (@0479, DET).
- Initial rollout strategy involves introducing the software to Scott McCann and West Region DETs to gain a second user and collect feedback and feature enhancement requests.

### **Course of Development**

**1. Event Management on Outlook Calendar**

   - **Add Events**:
     - `events.py`
     - Capture Event Start and End dates.
     - Status: Done!

   - **Schedule Labor**:
     - Associated with an event for accurate cost analysis.
     - Scheduled by dates 
     - Provide functionality to both schedule and cancel labor associated with an event.

**2. Worker Database**

   - All worker details, including contact information, skillsets, and weight, are stored in `labor.json`.
   - Weight, as a metric, assesses the appropriateness of workers based on reliability, compatibility, and skills. 

**3. Worker Selection Mechanism**

   - Consults the `labor.json` file to filter and rank workers.
   - Preference is given to those with a higher weight. In the event of a tie, the user will be informed and asked to choose a preferred worker.
   - Once identified, workers are notified via SMS through Twilio.

### **Technical Details**

**Programming Language**: Python

**Libraries/Frameworks**:

   - **Outlook Interaction**: `win32com` for the Outlook API.
   - **SMS Notifications**: Twilio's official Python SDK.

### **Application Architecture**

**1. Data Flow**:

   - The system captures user input from the CLI.
   - It interacts with Outlook using `win32com`, pushing or pulling event data as needed.

**2. Modular Design**:

   - Modules to be developed for:
     - Calendar Interactions
     - Worker Selection
     - Messaging

### **User Experience**

**1. Interface**: Command Line Interface (CLI)

**2. Input Validation**:

   - Ensure that date formats for event scheduling are valid.
   - Skillset inputs should match available skillsets.
   - A warning should be displayed if the labor scheduled exceeds the budget, e.g., "You're exceeding the labor budget. Please review the scheduled hours or adjust the budget accordingly." However, the user can choose to proceed if they wish.
   - Labor budgets are associated with a job through manual entry.
   - Labor cost is standardized at $110 an hour.

### **Script Flow**

A systematic series of questions that the user will be guided through during the labor scheduling process. This ensures that the labor is accurately aligned with the events listed in the Outlook calendar.

### **Proposed Series of Questions for Labor Scheduling**

**1. "Which date are you scheduling labor for?"**
   - The system fetches all events from the Outlook calendar for that specific date.
   
**2. "Here are the events for [selected date]. Which event are you scheduling labor for?"** 
   - The system displays a list of events for the user to select from.
   - For clarity, the list can display event names alongside their start and end times.
   
**3. "For the event '[selected event]', on which specific days do you need labor?"** 
   - Given that events can span multiple days, the system lists out each day of the event.
   - The user can select one or multiple days.
   
**4. "For [selected day/date], what is the start time for the labor shift?"**
   - The user specifies the starting time for the labor on that particular day.

**5. "And, what is the end time for the labor shift on [selected day/date]?"**
   - The user specifies the ending time for the labor on that day.

*(If the user selected multiple days in Step 3, repeat Steps 4 and 5 for each selected day.)*

**6. "What positions are you looking to schedule for this shift?"**
   - The user can select from a list of positions or specify a new one.

**7. "How many individuals do you need for each of the selected positions?"**
   - The user specifies the number of workers for each position.

**8. "Would you like to schedule another shift for a different position or day for the same event?"**
   - If 'Yes', return to the appropriate step based on the user's needs (e.g., if they want to schedule for another day, return to Step 3).
   - If 'No', the system proceeds to finalize the labor scheduling process.

**9. "Finalize the scheduled labor for '[selected event]' on [dates]?"**
   - This serves as a confirmation step before the actual scheduling action is taken.

**10. Once labor is finalized, the system would proceed with the selection mechanism based on weight, availability, and other criteria. If there's a tie or any decision to be made, the system would prompt accordingly.**


**11. Message candidates using the Twilio library and ask, "Are you available on [date] for [position]?" When workers respond with a yes or no, it's crucial to track their availability. This ensures that the system doesn't repeatedly contact workers who have already declined for specific dates. Here's a potential mechanism:

Availability Database:
Store the responses of workers in a database is a simple JSON file (availability.json), similar to your labor.json.

The availability.json file can have the following structure:

{
    "YYYY-MM-DD": {
        "Worker_ID_1": "yes",
        "Worker_ID_2": "no",
        "Worker_ID_3": "yes",
        ...
    },
    "YYYY-MM-DD": {
        ...
    }
}

In this structure:

The top-level keys are dates (the specific days for which labor is required).
For each date, there's a nested dictionary. This dictionary holds the worker IDs (or names) as keys and their availability responses ("yes" or "no") as values.
Usage:
Storing Availability:

When a worker responds with their availability, the system can update this file. If they respond with "yes," the system then proceeds to add them to the calendar.
If they respond with "no," it's added to the availability.json file. This ensures they're not contacted again for the same date.
Checking Availability Before Contacting:

Before the system contacts a worker, it can check availability.json for their response for that specific date. If there's a "no" already recorded or if they are already booked (a "yes"), the system skips contacting them.
Reset Mechanism:

Given the dynamic nature of scheduling and availabilities, implement a mechanism to reset availabilities for specific dates or events.

Archiving:

To avoid the file growing too large over time, you could archive older entries. For example, every month, the system could move the last month's entries to an archive file (availability_archive.json). This maintains a record of past availabilities without cluttering the main file.

### **5. User Experience**:

#### **Auto-Suggestions**:

Auto-suggestions can significantly enhance the CLI experience. By predicting what the user might type next based on their previous inputs and the context, it can save time and reduce errors. Here's how it could work:

- When specifying a **date**: If events are commonly scheduled on specific days (like every Monday), the system can suggest the upcoming Monday's date first.
  
- For **worker skillsets**: As the user begins typing a skillset, the system can display matching skillsets from `labor.json`.

Implementing auto-suggestions in a CLI can be achieved with libraries like `prompt_toolkit`.

#### **Budget Status**:

Providing a real-time budget status as "hours remaining" is a great idea. It gives the user immediate feedback about the labor hours they've allocated versus what's left in their budget. Here's how it could be integrated:

1. **Configuration File for Each Event** (`event_config.json`):

   ```json
   {
       "Event_Name_1": {
           "total_hours": 24,
           "consumed_hours": 16
       },
       "Event_Name_2": {
           ...
       }
   }
   ```

2. **User Interaction**:

   - When initiating the labor scheduling process, the system can ask: "Enter the total labor hours budget for [selected event]:". The response updates or sets the `total_hours` for that event in `event_config.json`.
   
   - As labor gets scheduled, the system updates `consumed_hours`. After each scheduling action, the system calculates the remaining hours (`total_hours` - `consumed_hours`) and displays it: "Eight of 24 hours remain in the budget."

3. **Exceeding the Budget**:

   - If the user's scheduling action would exceed the available hours, a warning can be displayed: "This action exceeds the labor budget by X hours. Do you wish to proceed?"

   - The user can then decide whether to continue with that action, adjust their labor hours, or make other modifications to stay within the budget.

### **5. User Experience**:

- When specifying a **date**: If events are commonly scheduled on specific days (like every Monday), the system can suggest the upcoming Monday's date first.
  
- For **worker skillsets**: As the user begins typing a skillset, the system can display matching skillsets from `labor.json`.

Implementing auto-suggestions in a CLI can be achieved with libraries like `prompt_toolkit`.

#### **Budget Status**:

Provide real-time budget status as "hours remaining". It gives the user immediate feedback about the labor hours they've allocated versus what's left in their budget. Here's how it could be integrated:

1. **Configuration File for Each Event** (`event_config.json`):

   ```json
   {
       "Event_Name_1": {
           "total_hours": 24,
           "consumed_hours": 16
       },
       "Event_Name_2": {
           ...
       }
   }
   ```

2. **User Interaction**:

   - When initiating the labor scheduling process, the system can ask: "Enter the total labor hours budget for [selected event]:". The response updates or sets the `total_hours` for that event in `event_config.json`.
   
   - As labor gets scheduled, the system updates `consumed_hours`. After each scheduling action, the system calculates the remaining hours (`total_hours` - `consumed_hours`) and displays it: "Eight of 24 hours remain in the budget."

3. **Exceeding the Budget**:

   - If the user's scheduling action would exceed the available hours, a warning can be displayed: "This action exceeds the labor budget by X hours. Do you wish to proceed?"

   - The user can then decide whether to continue with that action, adjust their labor hours, or make other modifications to stay within the budget.

Absolutely, integrating an "edit" or "go back" feature is a valuable addition, especially for a CLI application. This provides users with the flexibility to correct or change their inputs without the need to restart, making the tool more user-friendly.

### **6. Script Flow with Edit/Go Back Feature**:

#### **Implementation Strategy**:

Instead of a linear progression, consider the script flow as a series of steps or stages. After each step, users can proceed forward, edit their current selection, or go back to a previous step. A loop mechanism can manage the steps, allowing users to move back and forth until they're satisfied with their inputs.

#### **Flow**:

1. **"Which date are you scheduling labor for?"**
   - After date input, provide options: `[Continue, Edit Date, Exit]`

2. **"Here are the events for [selected date]. Which event are you scheduling labor for?"**
   - After event selection, options: `[Continue, Edit Event, Go Back to Date Selection, Exit]`

3. **"For the event '[selected event]', on which specific days do you need labor?"**
   - After day selection, options: `[Continue, Edit Days, Go Back to Event Selection, Exit]`

... and so on for each step in the flow.

#### **Error Handling & Validation**:

- If the user makes an input error in a step (like entering an invalid date format), immediately prompt them to correct it before moving to the next step.
  
- For selections like choosing a worker or skillset, list out available options and allow users to select from them to reduce input errors.

#### **Finishing Up**:

Once all selections are made, a summary screen can display all the choices made by the user. This provides a final opportunity to review and confirm or make edits:

- **Summary**:
  - **Date**: XYZ
  - **Event**: ABC
  - **Scheduled Hours**: 10
  ... 
   
   Options: `[Confirm and Proceed, Edit, Exit]`

If they choose to edit, the system can prompt: "Which detail would you like to edit? [Date, Event, Scheduled Hours, ...]". Then, it would take the user directly to that step.

Incorporating this feature requires slightly more complex flow control in the script but significantly enhances user experience and reduces potential frustration from input errors or changes of mind.

### **Error Handling**

- If there's an issue accessing the Outlook calendar, display: "Error accessing Outlook calendar. Please ensure Outlook is running and accessible."
- If there's a problem sending a message via Twilio, display: "Error sending SMS. Please check your Twilio configuration."
- If `labor.json` is malformed or unreadable, show: "Error reading worker data. Please ensure `labor.json` is present and properly formatted."
