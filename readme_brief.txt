
**2. Worker Database**
- **Details Stored**: All worker details, including contact information, skillsets, and weight, are cataloged in `labor.json`.
- **Weight Metric**: Weight is used to assess the appropriateness of workers. It's based on criteria such as reliability, compatibility, and skills.

**3. Worker Selection Mechanism**
- **Source**: The system refers to `labor.json` to filter and rank workers.
- **Weight Preference**: The system gives precedence to workers with higher weights. In case of ties in weight, the user will be prompted to select from the top contenders.
- **Notification**: Once workers are selected, they are informed about potential jobs via SMS through the Twilio platform.

### **Technical Details**
**Programming Language**: Python

**Libraries/Frameworks**:
- **Outlook Interface**: The system interfaces with the Outlook calendar using `win32com`.
- **SMS Platform**: For sending out SMS notifications, the system utilizes the Twilio Python SDK.

### **Application Architecture**
**1. Data Flow**:
- **User Input**: The system captures data directly from the CLI.
- **Outlook Interaction**: Based on the captured input, the system communicates with Outlook using `win32com`.

**2. Modular Design**:
- **Components**: The system is modular with distinct sections for Calendar Interactions, Worker Selection, and Messaging.

### **User Experience**
**1. Interface**: The primary user interface is the Command Line (CLI).

**2. Input Validation**:
- **Dates and Skillsets**: The system checks for valid date formats and ensures that skillset inputs match those available in the database.
- **Budget Alerts**: If the hours being scheduled exceed the budget, a warning message will pop up, allowing the user to make informed decisions.
- **Cost**: A standardized labor cost of $110/hour is used in budget calculations.

### **Script Flow**
The user is taken through a systematic series of questions, ensuring labor scheduling aligns with Outlook calendar events.

### **Proposed Series of Questions for Labor Scheduling**
(Here, the process is laid out step by step, from date selection to worker notification.)

**Availability Tracking**:
- **Database**: Workers' responses are tracked using `availability.json`.
- **Usage**: As workers confirm or decline availability, the system updates this database, ensuring that workers aren't contacted unnecessarily.

### **5. User Experience Enhancements**:

#### **Auto-Suggestions**:
- **Predictive Inputs**: To enhance the CLI experience, the system offers predictions, such as suggesting dates or matching skillsets.
- **Implementation**: This feature leverages `prompt_toolkit` for the CLI.

#### **Budget Status**:
- **Feedback**: As scheduling progresses, the user gets real-time updates on hours remaining in the budget.
- **Configuration**: Each event has an associated budget in `event_config.json`, which the system refers to for these updates.

### **6. Script Flow with Edit/Go Back Feature**:
- **Flexibility**: Users can navigate back to previous steps or edit inputs, allowing for adjustments without restarting the entire process.

### **Error Handling**
- **Errors Addressed**: The system is equipped to handle errors, such as issues accessing the Outlook calendar, problems with Twilio messaging, or reading the labor data.
