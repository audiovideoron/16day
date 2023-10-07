# calendar_ops.py

import win32com.client

def get_calendar_by_name(calendar_name):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    calendar = None

    for folder in outlook.GetDefaultFolder(9).Folders:
        if folder.Name == calendar_name:
            calendar = folder
            break

    return calendar

def create_calendar_event(calendar, subject, start, end, body=""):
    appointment = calendar.Items.Add(1)  # 1 represents olAppointmentItem
    appointment.Subject = subject
    appointment.Start = start
    appointment.End = end
    appointment.Body = body
    appointment.Save()

    return appointment
