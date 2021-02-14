from datetime import datetime


def getDateTime():
    now = datetime.now()
    current_time = now.strftime("%Y/%m/%d %H:%M:%S")
    return current_time


def printT(msg):
    print(f"[{getDateTime()}] {msg}")


def withinCheckPeriod(start_hour, end_hour):
    now = datetime.now()
    current_hour = now.strftime("%H")
    return start_hour <= int(current_hour) <= end_hour
