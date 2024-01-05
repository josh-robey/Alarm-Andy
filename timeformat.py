from datetime import datetime
from pytz import timezone

tz = timezone('America/New_York')


def update_time():
    st = str(str(datetime.now(tz).hour) + ":" + str(datetime.now(tz).minute))
    t = datetime.strptime(st, "%H:%M")
    current_hour = int(datetime.strftime(t, "%#I"))
    current_min = int(datetime.strftime(t, "%M"))
    am_pm = datetime.strftime(t, "%p")
    return current_hour, current_min, am_pm.lower()
