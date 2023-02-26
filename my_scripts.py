import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import json


def get_day_suffix(day):
    # Helper function to get the suffix for a day of the month
    if 11 <= day <= 13:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def format_date(date_string):
    # Parse the date string into a datetime object
    date = datetime.strptime(date_string, '%Y-%m-%d')

    # Format the date using the desired string format
    weekday = date.strftime('%A')
    day_suffix = get_day_suffix(date.day)
    month = date.strftime('%B')
    year = date.year
    formatted_date = f"{weekday}, {date.day}{day_suffix} {month}, {year}"
    
    return formatted_date


def emailer(info):
    with open("feedback.json", "r") as fileh:
        feedback_json = json.load(fileh)

    msg = f'Reported by; {info["name"]}\nReporter Email; {info["email"]}\
    \nReporter Number; {info["number"]}\n\n{info["message"]}'

    feedback_json[str(datetime.now())] = msg

    with open("feedback.json", "w") as fileh:
        json.dump(feedback_json, fileh)


def convert_from_24(hour):
    if str(hour) == '0' or str(hour) == '00':
        return "12AM"
    elif int(str(hour)) < 12:
        return str(hour) + 'AM'
    elif int(str(hour)) == 12:
        return str(hour) + 'PM'
    elif int(str(hour)) > 12:
        return str(int(str(hour)) - 12) + 'PM'


def hour_handler(hours):
    hours = str(hours)
    hr_list =hours.split(', ')
    if len(hr_list) == 1:
        return convert_from_24(hr_list[0])

    hr_list = [int(hr) for hr in hr_list]
    hr_list.sort()
    formatted_hrs = [convert_from_24(str(hr)) for hr in hr_list]
    return formatted_hrs[0] + '-' + formatted_hrs[-1]

def kmh_to_ms(speed):
    """
    Convert speed from kilometers per hour (km/h) to meters per second (m/s).
    """
    return round(speed * 1000 / 3600, 2)


def wind_type(deg, launcher_dir):
    deg = round(deg)
    half = 0
    if deg in range(0, 46) or deg in range(315, 360):
        half = 1
    elif deg in range(135, 181) or deg in range(180, 226):
        half = 3
    else:
        half = 2

    if launcher_dir == 'north':
        if half == 1:
            return 'Headwind'
        elif half == 2:
            return 'Crosswind'
        elif half == 3:
            return 'Tailwind'
    elif launcher_dir == 'south':
        if half == 3:
            return 'Headwind'
        elif half == 2:
            return 'Crosswind'
        elif half == 1:
            return 'Tailwind'
    else:
        return 'None'
