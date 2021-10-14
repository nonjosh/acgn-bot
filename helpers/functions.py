from datetime import datetime


def print_t(msg):
    now = datetime.now()
    current_time = now.strftime("%Y/%m/%d %H:%M:%S")
    print(f"[{current_time}] {msg}")


def within_check_period(start_hour, end_hour):
    now = datetime.now()
    current_hour = now.strftime("%H")
    return start_hour <= int(current_hour) <= end_hour
