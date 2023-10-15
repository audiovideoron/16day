from datetime import datetime

def get_scheduled_labor_date(year, month, day):
    try:
        date = datetime(year, month, day)
        return date.strftime('%Y-%m-%d')
    except ValueError:
        return "Invalid date"

# Example usage:
year, month, day = 2022, 12, 1
print(get_scheduled_labor_date(year, month, day))  # outputs: 2022-12-01
