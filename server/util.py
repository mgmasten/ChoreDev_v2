import uuid
import hashlib
from datetime import datetime, timedelta
import calendar
import server.constants as constants

def md5(string):
    hashObject = hashlib.md5(string.encode('utf-8'))
    return hashObject.hexdigest()

def generate_uuid():
    '''Helper function to generate a UUIDv4'''
    return uuid.uuid4()

def start_of_week():
    current = datetime.now()
    difference_in_days = (current.weekday() + 1) % constants.DAYS_IN_WEEK
    sunday = current - timedelta(days = difference_in_days)
    return datetime(sunday.year, sunday.month, sunday.day, 0, 0, 0, 0)

def start_of_month():
    current = datetime.now()
    return datetime(current.year, current.month, 1, 0, 0, 0, 0)

def now():
    return datetime.now()
def weekday_abbreviation():
    return list(calendar.day_abbr)[datetime.now().weekday()]
