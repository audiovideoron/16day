Job Tracker

Usable with features 1, 2 and 3. Ron Parker @0479, DET and Job Tracker 
developer is the first user. Introduce software to Scott McCann and 
West Region DETs to solicit a second user, feedback and feature requests. 

Course of Development
1. Add events to Outlook calendar
    A. Event Start, Event End
Done!

2. Schedule labor (per event for cost analysis)
    Script asks, 
    event_date = "What date?"
    event_name = "What is the event name?" (pick from list)
    event_set_date = "What day are you setting 'event_name'?"
    positions = "What positions are you looking for?" (choose one or more, and how many for that position)

   if positions v1, hand(3), crew_chief
    prospect = v1.labor.config && highest weight available
    for prospects
        if contact not booked on event (read calendar)
            event_candidate[] = prospect (build a list)
            for event_candidate
                twilio Are you date start, end time?


    Priority weight; if v1 and greater weight then message
    before v1 with lesser weight.

3. Add contacts
    consider modifying is_valid_phone_number(phone): to format to e164
    a seperate conversion function in our twilio code is probably preferable
Done.

Twilio 
    Automate labor messaging
    Disclaimer
        Start/End times are subject to change
3. Generate folders under documents/2023/current_month/client_name
4. Read BEOs into ChatGPT for summation, 
5. Bring Job Tracker to BEO meetings

Notes:
4. requires python to ChaptGPT API calls and needs to be paid for by Inspire.