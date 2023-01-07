import datetime
import calendar
from dateutil.relativedelta import relativedelta
import re
import math
import json
import database as db

today = datetime.date.today()
today_day_of_week = calendar.day_name[today.weekday()]
next_year = (datetime.date.today() + relativedelta(years=1)).year
days_in_this_year = 365 + calendar.isleap(today.year)
day_of_year = datetime.datetime.now().timetuple().tm_yday
days_remaining_in_year = days_in_this_year - day_of_year


def strtodate(str_date):
    return datetime.datetime.strptime(str_date, "%Y-%m-%d").date()


def add_year_if_anniversary_in_the_past(date_to_check):
    entry_date = date_to_check
    if today > date_to_check:
        entry_date = date_to_check.replace(year=today.year)
    if today > entry_date:
        entry_date = date_to_check.replace(year=next_year)
    return entry_date


def check_input_date(date):
    date_pattern = re.compile(r"^\d{4}\-(0[1-9]|1[012])\-(0[1-9]|[12][0-9]|3[01])$")
    date_checked = date_pattern.fullmatch(date)
    return date_checked


def time_difference_details(data):
    formatted_string = ''
    if abs(data.years) != 0:
        if abs(data.years) == 1:
            formatted_string += f"{abs(data.years)} year "
        else:
            formatted_string += f"{abs(data.years)} years "
    if abs(data.months) != 0:
        if abs(data.months) == 1:
            formatted_string += f"{abs(data.months)} month "
        else:
            formatted_string += f"{abs(data.months)} months "
    if abs(data.years) == 0 and abs(data.months) == 0:
        if abs(data.days) == 0:
            formatted_string = "Today"
        elif abs(data.days) == 1:
            formatted_string = "Tomorrow"
        else:
            formatted_string += f"{abs(data.days)} days"
    else:
        if abs(data.days) != 0:
            if abs(data.days) == 1:
                formatted_string += f"{abs(data.days)} day"
            else:
                formatted_string += f"{abs(data.days)} days"
    return formatted_string


def calculate_easter(year_to_check):
    easter_dates = ["3-27", "4-14", "4-3", "3-23", "4-11", "3-31", "4-18", "4-8", "3-28", "4-16", "4-5", "3-25", "4-13", "4-2", "3-22", "4-10", "3-30", "4-17", "4-7", "3-27"]
    a = (year_to_check - math.floor(year_to_check / 19) * 19) + 1
    date_to_check = datetime.datetime.strptime(f"{year_to_check}-{easter_dates[a]}", "%Y-%m-%d").date()
    days_difference = (6 - date_to_check.weekday()) % 7
    easter_date = date_to_check + datetime.timedelta(days=days_difference)
    return easter_date


def json_export():
    an_lst = []
    data_an = db.get_all_items('anniversaries')
    dates_as_anniversaries = db.get_dates_as_anniversaries()
    for ann in data_an:
        an_lst.append(ann)
    for da in dates_as_anniversaries:
        an_lst.append(da)
    an_lst.sort(key=lambda x: x[2])
    an_list = []
    ev_list = []
    for a in an_lst:
        an_list.append([a[0], a[1]])
    for e in db.get_all_items('events'):
        ev_list.append([e[0], e[1]])
    all_exports = {'anniversaries': an_list, 'events': ev_list}
    with open("json_export.json", "w", encoding="utf-8") as file:
        json.dump(all_exports, file, indent=2, ensure_ascii=False)


def clear_entry_placeholders(widget):
    widget.delete(0, "end")
    widget.unbind("<Button-1>")
    widget.unbind("<FocusIn>")


def unbind_everything(widget):
    widget.unbind("<Delete>")
    widget.unbind("<Button-2>")
    widget.unbind("<MouseWheel>")
    widget.unbind("<Left>")
    widget.unbind("<Delete>")
    widget.unbind("<Delete>")
    widget.unbind("<Delete>")
