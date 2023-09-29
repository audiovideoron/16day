Job Tracker

Usable with features 1 and 2. Ron Parker @0479, DET and Job Tracker 
developer is the first user. Introduce software to Scott McCann and 
West Region DETs to solicit a second user, feedback and feature requests. 

Course of Development
1. Add events to Outlook calendar
    A. Event Start, Event End
2. Book labor for events
    Use config files to store contacts and track event bookings. If 
    person isn't booked put them in the call list. Assign skillset 
    and priority weight to each person; if v1 and priority 1 message
    before v1 priority 2.
    A. Twilio to automate labor messaging
    B. Start/End times are subject to change
3. Generate folders under documents/2023/current_month/client_name
4. Read BEOs into ChatGPT for summation, 
5. Bring Job Tracker to BEO meetings

State of Development
1. usable, but Start/End isn't infallible
2. has been started and development will begin focusing on it
3. not required for first release
4. not required for first release
5. close
6. Inspire needs to buy Salesforce License for every site
7. Inspire needs to buy license for twilio

Notes:
4. requires python to ChaptGPT API calls and needs to be paid for by Inspire.

Early Version

SMS
The body of the calendar entry must follow this format. Any deviation breaks the interface.

date_range: 2023-09-11 – 2023-09-13
1 lead; Josiah, Dana, Phoenix
1 hand; Joe Sullivan, Logan, Lisa

date_range: 2023-09-11
1 lead; Josiah, Dana
1 hand; Logan, Lisa

TODO
1. Design updates for contacts