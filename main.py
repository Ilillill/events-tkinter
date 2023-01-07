import tkinter as tk
from tkinter import ttk
import pickle
from tkinter import font, messagebox
import sqlite3

import calendar
from dateutil.relativedelta import relativedelta

import database as db
import logic as lg

from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)


try:
    with open("./databases/database_data.dat", "rb") as file:
        database_name = pickle.load(file)
except FileNotFoundError:
    database_name = ''

ACCENT = "#829460"
BUTTON_BG = "#3C4048"
BUTTON_FG = "#F9F7F7"
LABEL_BG = "#F9F7F7"
LABEL_FG = "#3C4048"
FRAME_BG = "#F9F7F7"
WARNING_COLOUR = 'orange'


class Limiter(tk.Frame):
    def __init__(self, container, data, which_table, widgets_per_window=10):
        super().__init__(container)
        self.data = data
        self.which_table = which_table
        self.widgets_per_window = widgets_per_window
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.configure(bg=FRAME_BG)
        lg.unbind_everything(root)

        if self.data:
            self.your_birthday = None
            if db.get_all_items('you'):
                self.you_data = db.get_all_items('you')[0]
                self.your_birthday = lg.strtodate(self.you_data[1])

            self.divided_data = [self.data[x:x+self.widgets_per_window] for x in range(0, len(self.data), self.widgets_per_window)]
            self.chunks_number = len(self.divided_data)
            self.divided_data_index = 0

            self.frame_labels = tk.Frame(self, bg=FRAME_BG)
            self.frame_labels.grid(row=0, column=0, sticky="NEWS")
            self.frame_labels.columnconfigure(0, weight=1)

            if len(self.data) > self.widgets_per_window:
                root.bind("<Delete>", lambda event: self.reset_screen())
                root.bind("<Button-2>", lambda event: self.reset_screen())
                self.frame_buttons = tk.Frame(self, bg=FRAME_BG)
                self.frame_buttons.grid(row=1, column=0, sticky="EW")
                self.frame_buttons.columnconfigure((0, 4), weight=1)

                self.button_previous = tk.Button(self.frame_buttons, text="Previous", state="disabled", command=lambda: self.previous_screen(), width=20, font=font_menu_buttons, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat")
                self.button_previous.grid(row=0, column=0, sticky="E")

                self.button_reset = tk.Button(self.frame_buttons, text=f"Reset", command=lambda: self.reset_screen(), width=20, font=font_menu_buttons, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat")
                self.button_reset.grid(row=0, column=1)
                self.button_next = tk.Button(self.frame_buttons, text="Next", command=lambda: self.next_screen(), width=20, font=font_menu_buttons, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat")
                self.button_next.grid(row=0, column=2, sticky="W")
                root.bind("<Right>", lambda event: self.next_screen())
                root.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "right"))

            self.font_number_of_days = font.Font(family="Segoe Print", size=16, weight="bold")
            self.font_details = font.Font(family="Segoe Print", size=12)
            self.prepare_widgets(self.divided_data_index)

            if self.which_table != "durations":
                statusbar.set(f"Page {self.divided_data_index+1} / {self.chunks_number} | Total entries: {len(self.data)}")

    def mouse_scroll(self, event, allowed_direction):
        if allowed_direction == 'both':
            if event.delta < 0:
                self.next_screen()
            else:
                self.previous_screen()
        if allowed_direction == 'right':
            if self.divided_data_index < self.chunks_number-1:
                if event.delta < 0:
                    self.next_screen()
        else:
            if self.divided_data_index > 0:
                if event.delta > 0:
                    self.previous_screen()

    def next_screen(self):
        self.button_previous["state"] = 'normal'
        root.bind("<Left>", lambda event: self.previous_screen())
        root.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "both"))
        self.divided_data_index += 1
        self.prepare_widgets(self.divided_data_index)
        if self.divided_data_index == self.chunks_number-1:
            self.button_next["state"] = 'disabled'
            root.unbind("<Right>")
            root.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "left"))

    def previous_screen(self):
        self.button_next["state"] = 'normal'
        root.bind("<Right>", lambda event: self.next_screen())
        root.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "both"))
        self.divided_data_index -= 1
        self.prepare_widgets(self.divided_data_index)
        if self.divided_data_index == 0:
            self.button_previous["state"] = "disabled"
            root.unbind("<Left>")
            root.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "right"))

    def reset_screen(self):
        self.divided_data_index = 0
        self.button_next["state"] = 'normal'
        root.bind("<Right>", lambda event: self.next_screen())
        root.bind("<MouseWheel>", lambda event: self.mouse_scroll(event, "right"))
        self.button_previous["state"] = "disabled"
        root.unbind("<Left>")
        self.prepare_widgets(self.divided_data_index)

    def prepare_widgets(self, main_index):
        for child in self.frame_labels.winfo_children():
            child.destroy()
        if self.data:
            if self.which_table != "durations":
                statusbar.set(f"Page {self.divided_data_index+1} / {self.chunks_number} | Total entries: {len(self.data)}")
            if self.which_table == "durations":
                for index, d in enumerate(self.divided_data[main_index]):
                    self.create_durations(index, d)

            elif self.which_table == "diary":
                for index, d in enumerate(self.divided_data[main_index]):
                    self.create_diary(index, d)
            else:
                for index, d in enumerate(self.divided_data[main_index]):
                    self.create_dates(index, d)

    def create_diary(self, position, dt):
        frame_group = tk.Frame(self.frame_labels, bg=FRAME_BG)
        frame_group.grid(row=position, column=0, sticky='news')
        frame_group.columnconfigure(1, weight=1)
        frame_date = tk.Frame(frame_group, bg=FRAME_BG)
        frame_date.grid(row=0, column=0, sticky='w')
        dates_text = str(abs((lg.today - dt[1]).days))
        button_days = tk.Button(frame_date, width=10, text=dates_text, bg=LABEL_BG, fg=LABEL_FG, font=font_number_of_days, borderwidth=0, relief="flat", activebackground=LABEL_BG)
        button_days.grid(row=0, column=0, sticky="ew")
        button_days['command'] = lambda: FrameAddUpdateDiary(root, data=dt)
        label_details = tk.Label(frame_date, bg=LABEL_BG, fg=LABEL_FG, text=f"{calendar.day_name[dt[1].weekday()]} ⋮ {dt[1].year}.{dt[1].month}.{dt[1].day}", font=font_date_details)
        label_details.grid(row=1, column=0)
        label_in_months = tk.Label(frame_date, bg=LABEL_BG, fg=LABEL_FG, width=30, text=f"{lg.time_difference_details(relativedelta(dt[1], lg.today))}", font=font_date_details)
        label_in_months.grid(row=2, column=0)
        font_options = font.Font(family='Arial', size=8, slant="italic")
        if (dt[1] - self.your_birthday).days > 0:
            label_how_old = tk.Label(frame_date, bg=LABEL_BG, fg=LABEL_FG, font=font_options, text=f"🎂 {lg.time_difference_details(relativedelta(self.your_birthday, dt[1]))}")
            label_how_old.grid(row=3, column=0, sticky="ew")
        frame_details = tk.Frame(frame_group, bg=FRAME_BG)
        frame_details.grid(row=0, column=1, sticky='news')
        frame_details.rowconfigure(0, weight=1)
        frame_details.columnconfigure(0, weight=1)
        label_description_text = dt[0]
        label_description = tk.Label(frame_details, text=label_description_text, bg=LABEL_BG, fg=LABEL_FG, anchor="w", borderwidth=0, relief="flat", activebackground=LABEL_BG, font=font_event_name, wraplength=720)
        label_description.grid(row=0, column=0, sticky="new", pady=(30, 0))
        label_options_text = ''
        label_options = tk.Label(frame_details, text=label_options_text, bg=LABEL_BG, fg=LABEL_FG, font=font_date_details)
        label_options.grid(row=1, column=0, sticky="ws")
        if dt[3]:
            time_beginning = dt[1]
            time_end = dt[3]
            time_days = str(abs((dt[1]-dt[3]).days))
            time_days_formatted = lg.time_difference_details(relativedelta(time_beginning, time_end))
            label_options.configure(text=f"⏳ {time_days_formatted} ⋮ {time_beginning.year}.{time_beginning.month}.{time_beginning.day} - {time_end.year}.{time_end.month}.{time_end.day} ⋮ {time_days}")
        ttk.Separator(frame_group).grid(row=1, column=0, columnspan=2, sticky='ew')

    def create_durations(self, position, dt):
        frame_details = tk.Frame(self.frame_labels, bg=FRAME_BG)
        frame_details.grid(row=position, column=0, sticky='news')
        frame_details.columnconfigure(1, weight=1)
        label_previous = tk.Label(frame_details, bg=LABEL_BG, fg=LABEL_FG, width=35, text=f"{dt[0][0]}\n{dt[0][1]}", wraplength=300)
        label_previous.grid(row=0, column=0, sticky="ew", rowspan=2)
        label_difference = tk.Label(frame_details, bg=LABEL_BG, fg=LABEL_FG, font=self.font_number_of_days, text=(lg.strtodate(dt[1][1]) - lg.strtodate(dt[0][1])).days, width=6)
        label_difference.grid(row=0, column=1)
        label_difference_details = tk.Label(frame_details, bg=LABEL_BG, fg=LABEL_FG, font=font_menu_buttons, width=25, text=lg.time_difference_details(relativedelta(lg.strtodate(dt[1][1]), lg.strtodate(dt[0][1]))))
        label_difference_details.grid(row=1, column=1)
        label_next = tk.Label(frame_details, bg=LABEL_BG, fg=LABEL_FG, width=35, text=f"{dt[1][0]}\n{dt[1][1]}", wraplength=300)
        label_next.grid(row=0, column=2, sticky="ew", rowspan=2)
        ttk.Separator(frame_details).grid(row=2, column=0, columnspan=3, sticky="ew")

    def create_dates(self, position, dt):
        frame_group = tk.Frame(self.frame_labels, bg=FRAME_BG)
        frame_group.grid(row=position, column=0, sticky='news')
        frame_group.columnconfigure(1, weight=1)
        frame_date = tk.Frame(frame_group, bg=FRAME_BG)
        frame_date.grid(row=0, column=0, sticky='w')
        dates_text = str(abs((lg.today - dt[2]).days))
        button_days = tk.Button(frame_date, width=10, text=dates_text, bg=LABEL_BG, fg=LABEL_FG, font=font_number_of_days, borderwidth=0, relief="flat", activebackground=LABEL_BG)
        button_days['command'] = lambda: FrameAddUpdate(root, data=dt, which_table=self.which_table)
        button_days.grid(row=0, column=0, sticky="ew")
        label_details = tk.Label(frame_date, bg=LABEL_BG, fg=LABEL_FG, text=f"{calendar.day_name[dt[2].weekday()]} ⋮ {dt[2].year}.{dt[2].month}.{dt[2].day}", font=font_date_details)
        label_details.grid(row=1, column=0)
        label_in_months = tk.Label(frame_date, bg=LABEL_BG, fg=LABEL_FG, width=30, text=f"{lg.time_difference_details(relativedelta(dt[2], lg.today))}", font=font_date_details)
        label_in_months.grid(row=2, column=0)
        frame_details = tk.Frame(frame_group, bg=FRAME_BG)
        frame_details.grid(row=0, column=1, sticky='news')
        frame_details.rowconfigure(0, weight=1)
        frame_details.columnconfigure(0, weight=1)
        label_description_text = dt[1]
        label_description = tk.Label(frame_details, text=label_description_text, bg=LABEL_BG, fg=LABEL_FG, anchor="w", borderwidth=0, relief="flat", activebackground=LABEL_BG, font=font_event_name, wraplength=720)
        label_description.grid(row=0, column=0, sticky="new", pady=(30, 0))
        if len(dt[3]) > 0:
            label_description_text += " [...]"
            label_description['text'] = label_description_text
        font_options = font.Font(family='Arial', size=8, slant="italic")
        font_options_warning = font.Font(family='Arial', size=6, slant="italic")
        label_options_text = ''
        label_options = tk.Label(frame_details, text=label_options_text, bg=LABEL_BG, fg=LABEL_FG, font=font_options)
        label_options.grid(row=1, column=0, sticky="ws")
        if self.which_table == 'dates':
            your_birthday = lg.strtodate(db.get_all_items('you')[0][1])
            if (dt[2] - your_birthday).days > 0:
                label_how_old = tk.Label(frame_date, bg=LABEL_BG, fg=LABEL_FG, font=font_options, text=f"🎂 {lg.time_difference_details(relativedelta(your_birthday, dt[2]))}")
                label_how_old.grid(row=3, column=0, sticky="ew")
            if dt[-3]:
                label_options_text += "Durations "
                label_options['text'] = label_options_text
            if dt[-2]:
                label_options_text += "Anniversaries "
                label_options['text'] = label_options_text
        if self.which_table == 'anniversaries':
            if dt[-1] != 'anniversaries':
                label_options.configure(text="added from dates", fg=WARNING_COLOUR, font=font_options_warning)
                button_days.config(command=lambda: None)
        ttk.Separator(frame_group).grid(row=1, column=0, columnspan=2, sticky='ew')


class FrameMenu(tk.Frame):

    def __init__(self, container):
        super().__init__(container)
        lg.unbind_everything(root)
        self.columnconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        self.configure(bg=ACCENT)
        self.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.highlightthickness = 0
        self.b_home = tk.Button(self, text="Home", font=font_menu_buttons, bg=BUTTON_FG, fg=BUTTON_BG, relief="flat", activebackground=BUTTON_FG, width=30, command=lambda: [self.change_colour(self.b_home), FrameHome(root)])
        self.b_home.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.b_anniversaries = tk.Button(self, text="Anniversaries", font=font_menu_buttons, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", activebackground=BUTTON_FG, width=30, command=lambda: [self.change_colour(self.b_anniversaries), FrameDates(root, data=db.get_all_items('anniversaries'), which_table="anniversaries")])
        self.b_anniversaries.grid(row=0, column=1, sticky="ew", padx=(0, 2))
        self.b_events = tk.Button(self, text="Events", font=font_menu_buttons, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", activebackground=BUTTON_FG, width=30, command=lambda: [self.change_colour(self.b_events), FrameDates(root, data=db.get_all_items('events'), which_table="events")])
        self.b_events.grid(row=0, column=2, sticky="ew", padx=(0, 2))
        self.b_dates = tk.Button(self, text="Dates", font=font_menu_buttons, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", activebackground=BUTTON_FG, width=30, command=lambda: [self.change_colour(self.b_dates), FrameDates(root, data=db.get_all_items('dates'), which_table="dates")])
        self.b_dates.grid(row=0, column=3, sticky="ew", padx=(0, 2))
        self.b_diary = tk.Button(self, text="Diary", font=font_menu_buttons, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", activebackground=BUTTON_FG, width=30, command=lambda: [self.change_colour(self.b_diary), FramePersonalDiary(root, data=db.get_personal_diary_items())])
        self.b_diary.grid(row=0, column=4, sticky="ew", padx=(0, 2))
        self.b_durations = tk.Button(self, text="Durations", font=font_menu_buttons, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", activebackground=BUTTON_FG, width=30, command=lambda: [self.change_colour(self.b_durations), FrameDurations(root, data=db.get_durations())])
        self.b_durations.grid(row=0, column=5, sticky="ew", padx=(0, 2))
        self.b_settings = tk.Button(self, text="Settings", font=font_menu_buttons, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", activebackground=BUTTON_FG, width=30, command=lambda: [self.change_colour(self.b_settings), FrameSettings(root)])
        self.b_settings.grid(row=0, column=6, sticky="ew")

    def change_colour(self, widget):
        self.b_home.configure(bg=BUTTON_BG, fg=BUTTON_FG)
        self.b_anniversaries.configure(bg=BUTTON_BG, fg=BUTTON_FG)
        self.b_events.configure(bg=BUTTON_BG, fg=BUTTON_FG)
        self.b_dates.configure(bg=BUTTON_BG, fg=BUTTON_FG)
        self.b_diary.configure(bg=BUTTON_BG, fg=BUTTON_FG)
        self.b_durations.configure(bg=BUTTON_BG, fg=BUTTON_FG)
        self.b_settings.configure(bg=BUTTON_BG, fg=BUTTON_FG)
        widget.configure(bg=BUTTON_FG, fg=BUTTON_BG)


class FrameHome(tk.Frame):
    def __init__(self, container):
        super().__init__(container)
        self.columnconfigure(0, weight=1)
        self.configure(bg=FRAME_BG)
        self.grid(row=1, column=0, sticky='news')
        ttk.Separator(self).grid(row=0, column=0, pady=20, sticky="ew")
        frame_today = tk.Frame(self, bg=FRAME_BG)
        frame_today.grid(row=1, column=0, sticky='ew')
        frame_today.columnconfigure(0, weight=1)
        tk.Label(frame_today, text=f"{lg.today_day_of_week}", bg=LABEL_BG, fg=ACCENT, font=font_home_week).grid(row=0, column=0, sticky="ew")
        tk.Label(frame_today, text=f"{lg.today.year}.{lg.today.month}.{lg.today.day}", bg=LABEL_BG, fg=LABEL_FG, font=font_home_date).grid(row=1, column=0, sticky="ew")
        tk.Label(frame_today, text=f"{lg.day_of_year} day of the year, {lg.days_remaining_in_year} days left", bg=LABEL_BG, fg=LABEL_FG, font=font_date_details).grid(row=2, column=0, sticky="ew")
        ttk.Separator(self).grid(row=2, column=0, pady=20, sticky="ew")
        lg.unbind_everything(root)
        important_anniversaries = [
            {"icon": "🦇", "name": "Halloween", "date": "10-31"},
            {"icon": "🎄", "name": "Christmas", "date": "12-24"},
            {"icon": "🎇", "name": "New Year", "date": "1-1"},
            {"icon": "💞", "name": "Valentine's Day", "date": "2-14"},
            {"icon": "🌹", "name": "Women's Day", "date": "3-3"},
            {"icon": "🤪", "name": "April Fool's", "date": "4-1"},
            {"icon": "🤶", "name": "Mother's Day", "date": "5-10"},
            {"icon": "🧸", "name": "Children's Day", "date": "6-1"},
            {"icon": "🎅", "name": "Father's Day", "date": "6-21"},
            {"icon": "🐶", "name": "Dog's Day", "date": "8-26"},
            {"icon": "‍🙎", "name": "Men's Day", "date": "11-19"}
        ]
        easter_date = lg.calculate_easter(lg.today.year)
        if lg.today > easter_date:
            easter_date = lg.calculate_easter(lg.next_year)
        i = []
        for ian in important_anniversaries:
            i.append([ian['icon'], ian['name'], abs((lg.today-lg.add_year_if_anniversary_in_the_past(lg.strtodate(f"{lg.today.year}-{ian['date']}"))).days)])
        i.append(["🐇", "Easter", abs((lg.today-easter_date).days)])
        i.sort(key=lambda x: x[2])
        self.copylist = i.copy()
        frame_important = tk.Frame(self, bg=FRAME_BG)
        frame_important.grid(row=3, column=0, sticky="news")
        frame_important.columnconfigure((0, 1, 2, 3), weight=1)

        font_important_icon = font.Font(family="Times", size=40)
        font_important_days = font.Font(family="Segoe Print", size=24, weight="bold")
        font_important_details = font.Font(family="Merriweather", size=10)

        l0i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[0][0])
        l0i.grid(row=0, column=0)
        l0d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[0][2])
        l0d.grid(row=1, column=0)
        l0t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[0][1])
        l0t.grid(row=2, column=0, pady=(0, 50))

        l1i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[1][0])
        l1i.grid(row=0, column=1)
        l1d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[1][2])
        l1d.grid(row=1, column=1)
        l1t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[1][1])
        l1t.grid(row=2, column=1, pady=(0, 50))

        l2i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[2][0])
        l2i.grid(row=0, column=2)
        l2d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[2][2])
        l2d.grid(row=1, column=2)
        l2t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[2][1])
        l2t.grid(row=2, column=2, pady=(0, 50))

        l3i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[3][0])
        l3i.grid(row=0, column=3)
        l3d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[3][2])
        l3d.grid(row=1, column=3)
        l3t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[3][1])
        l3t.grid(row=2, column=3, pady=(0, 50))

        l4i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[4][0])
        l4i.grid(row=3, column=0)
        l4d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[4][2])
        l4d.grid(row=4, column=0)
        l4t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[4][1])
        l4t.grid(row=5, column=0, pady=(0, 50))

        l5i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[5][0])
        l5i.grid(row=3, column=1)
        l5d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[5][2])
        l5d.grid(row=4, column=1)
        l5t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[5][1])
        l5t.grid(row=5, column=1, pady=(0, 50))

        l6i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[6][0])
        l6i.grid(row=3, column=2)
        l6d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[6][2])
        l6d.grid(row=4, column=2)
        l6t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[6][1])
        l6t.grid(row=5, column=2, pady=(0, 50))

        l7i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[7][0])
        l7i.grid(row=3, column=3)
        l7d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[7][2])
        l7d.grid(row=4, column=3)
        l7t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[7][1])
        l7t.grid(row=5, column=3, pady=(0, 50))

        l8i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[8][0])
        l8i.grid(row=6, column=0)
        l8d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[8][2])
        l8d.grid(row=7, column=0)
        l8t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[8][1])
        l8t.grid(row=8, column=0, pady=(0, 50))

        l9i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[9][0])
        l9i.grid(row=6, column=1)
        l9d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[9][2])
        l9d.grid(row=7, column=1)
        l9t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[9][1])
        l9t.grid(row=8, column=1, pady=(0, 50))

        l10i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[10][0])
        l10i.grid(row=6, column=2)
        l10d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[10][2])
        l10d.grid(row=7, column=2)
        l10t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[10][1])
        l10t.grid(row=8, column=2, pady=(0, 50))

        l11i = tk.Label(frame_important, bg=LABEL_BG, fg=ACCENT, font=font_important_icon, text=i[11][0])
        l11i.grid(row=6, column=3)
        l11d = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_days, text=i[11][2])
        l11d.grid(row=7, column=3)
        l11t = tk.Label(frame_important, bg=LABEL_BG, fg=LABEL_FG, font=font_important_details, text=i[11][1])
        l11t.grid(row=8, column=3, pady=(0, 50))

        labels_list = [l0i, l1i, l2i, l3i, l4i, l5i, l6i, l7i, l8i, l9i, l10i, l11i]

        for index, lbl in enumerate(labels_list):
            self.create_bindings(lbl, index)

        frame_preview = tk.Frame(self, bg=FRAME_BG)
        frame_preview.grid(row=4, column=0, sticky='news')
        frame_preview.columnconfigure((0, 1), weight=1)
        frame_preview.rowconfigure(1, weight=1)

        tk.Label(frame_preview, bg=LABEL_BG, fg=LABEL_FG, text="Anniversaries", font=font_number_of_days).grid(row=0, column=0, sticky='ew')
        tk.Label(frame_preview, bg=LABEL_BG, fg=LABEL_FG, text="Events", font=font_number_of_days).grid(row=0, column=1, sticky='ew')

        self.frame_preview_anniversaries = tk.Frame(frame_preview, bg=FRAME_BG)
        self.frame_preview_anniversaries.grid(row=1, column=0, sticky='news')
        self.frame_preview_anniversaries.columnconfigure((0, 3), weight=1)

        self.an_lst = []
        data_an = db.get_all_items('anniversaries')
        dates_as_anniversaries = db.get_dates_as_anniversaries()
        for ann in data_an:
            new_date = lg.add_year_if_anniversary_in_the_past(lg.strtodate(ann[1]))
            self.an_lst.append([ann[-1], ann[0], new_date, ann[2], ann[3]])
        for da in dates_as_anniversaries:
            da_new_date = lg.add_year_if_anniversary_in_the_past(lg.strtodate(da[1]))
            self.an_lst.append([da[-1], da[0], da_new_date, da[2], da[3]])

        self.an_lst.sort(key=lambda x: x[2])

        an_lab_no = 10
        if len(self.an_lst) < 10:
            an_lab_no = len(self.an_lst)
        for lan in range(an_lab_no):
            self.create_labels(lan, self.frame_preview_anniversaries, self.an_lst)

        self.frame_preview_events = tk.Frame(frame_preview, bg=FRAME_BG)
        self.frame_preview_events.grid(row=1, column=1, sticky='news')
        self.frame_preview_events.columnconfigure((0, 3), weight=1)
        self.pr_ev = db.get_all_items('events')
        self.ev_lst = []
        for evv in self.pr_ev:
            new_e_date = lg.strtodate(evv[1])
            if new_e_date >= lg.today:
                self.ev_lst.append([evv[-1], evv[0], new_e_date, evv[2], evv[3]])
        ev_lab_no = 10
        if len(self.pr_ev) < 10:
            ev_lab_no = len(self.pr_ev)
        for lev in range(ev_lab_no):
            self.create_labels(lev, self.frame_preview_events, self.ev_lst)

        statusbar.set("Have a lovely day!")

    def create_labels(self, lan, cnt, data):
        tk.Label(cnt, bg=LABEL_BG, fg=LABEL_FG, text=(data[lan][2]-lg.today).days, font=font_event_name).grid(row=lan, column=1, sticky='e', padx=(0, 20))
        tk.Label(cnt, bg=LABEL_BG, fg=LABEL_FG, text=data[lan][1]).grid(row=lan, column=2, sticky='w')

    def create_bindings(self, b, p):
        b.bind("<Enter>", lambda event: statusbar.set(lg.today + relativedelta(days=self.copylist[p][2])))
        b.bind("<Leave>", lambda event: statusbar.set(""))


def confirm_expired_events_clear(list_of_ids):
    if messagebox.askyesno(title='Clear expired events', message="Are you sure you want to delete all expired events?"):
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            for event_to_delete in list_of_ids:
                cursor.execute(f"DELETE FROM events WHERE rowid={event_to_delete}")
            connection.commit()
            cursor.close()


def expired_events_window(widget):
    popup_window = tk.Toplevel()
    popup_window.geometry("1440x810")
    popup_window.rowconfigure(0, weight=1)
    popup_window.columnconfigure(0, weight=1)
    popup_window.configure(bg=FRAME_BG)
    popup_window.title('Expired Events')
    font_expired_events = font.Font(family="Arial", size=10)
    ids_list = []
    ev = db.get_all_items('events')
    text = tk.Text(popup_window, font=font_expired_events, bg=FRAME_BG)
    text.grid(row=0, column=0, sticky="NEWS")
    for index, e in enumerate(ev):
        if lg.strtodate(e[1]) < lg.today:
            text.insert(f"{index}.0", f'{e[1]} - {e[0]}\n')
            ids_list.append(e[-1])

    scrollbar = ttk.Scrollbar(popup_window, orient="vertical", command=text.yview)
    scrollbar.grid(row=0, column=1, sticky="NS")
    text["yscrollcommand"] = scrollbar.set
    frame_buttons = tk.Frame(popup_window, bg=FRAME_BG)
    frame_buttons.grid(row=2, column=0, sticky="EW", pady=10, padx=10)
    frame_buttons.columnconfigure(0, weight=1)
    if len(ids_list) != 0:
        popup_add_button = tk.Button(frame_buttons, text='Clear all expired events', command=lambda: [confirm_expired_events_clear(ids_list), popup_window.destroy(), statusbar.set("Expired Events removed successfully"), widget.configure(fg='grey', command=lambda: statusbar.set("No expired events"), text="Expired Events (0)")], width=30, bg=BUTTON_BG, fg=BUTTON_FG)

        popup_add_button.grid(row=0, column=1, sticky="w")
    popup_cancel_button = tk.Button(frame_buttons, text="Cancel", command=lambda: popup_window.destroy(), width=30, bg=BUTTON_BG, fg=BUTTON_FG)
    popup_cancel_button.grid(row=0, column=2, sticky="w")


def my_birthday_window():
    popup_window = tk.Toplevel()
    popup_window.rowconfigure(0, weight=1)
    popup_window.columnconfigure(0, weight=1)
    popup_window.configure(bg=FRAME_BG)
    popup_window.title('My birthday details')
    popup_window.resizable(False, False)

    d = []
    if db.get_all_items('you'):
        d = db.get_all_items('you')[0]
        my_data = [d[0], lg.strtodate(d[1]), d[2], d[3], d[4]]
        insert_font_colour = 'black'
    else:
        my_data = ["name", ["yyyy", "mm", "dd"], "note", "", ""]
        insert_font_colour = 'gray'

    frame_me = tk.Frame(popup_window, bg=FRAME_BG)
    frame_me.grid(row=0, column=0, sticky="news", padx=50, pady=(50, 50))
    frame_me.columnconfigure((0, 2), weight=1)
    frame_me.rowconfigure((0, 4), weight=1)
    date_frame = tk.Frame(frame_me, bg=FRAME_BG)
    date_frame.grid(row=1, column=1, sticky='ew')
    text_year_start = tk.Entry(date_frame, width=6, font=("Times", 10, "italic"), fg=insert_font_colour, bg=LABEL_BG)
    text_year_start.grid(row=0, column=0)
    text_year_start.insert(0, 'yyyy')
    tk.Label(date_frame, text="-", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=0, column=1)
    text_month_start = tk.Entry(date_frame, width=4, font=("Times", 10, "italic"), fg=insert_font_colour, bg=LABEL_BG)
    text_month_start.insert(0, 'mm')
    text_month_start.grid(row=0, column=2)
    tk.Label(date_frame, text="-", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=0, column=3)
    text_day_start = tk.Entry(date_frame, width=4, font=("Times", 10, "italic"), fg=insert_font_colour, bg=LABEL_BG)
    text_day_start.insert(0, 'dd')
    text_day_start.grid(row=0, column=4)
    entry_your_name = tk.Entry(frame_me, bg=FRAME_BG, width=20, fg=insert_font_colour, font=("Times", 12, "italic"))
    entry_your_name.grid(row=2, column=1, sticky='ew')
    entry_your_name.insert(0, 'name')
    entry_you_description = tk.Entry(frame_me, font=("Times", 8, "italic"), fg=insert_font_colour, bg=LABEL_BG, width=20)
    entry_you_description.grid(row=3, column=1, sticky='news', pady=5)
    entry_you_description.insert(0, 'note')

    if my_data == ["name", ["yyyy", "mm", "dd"], "note", "", ""]:
        text_year_start.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(text_year_start))
        text_year_start.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(text_year_start))
        text_month_start.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(text_month_start))
        text_month_start.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(text_month_start))
        text_day_start.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(text_day_start))
        text_day_start.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(text_day_start))
        entry_your_name.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(entry_your_name))
        entry_your_name.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(entry_your_name))
        entry_you_description.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(entry_you_description))
        entry_you_description.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(entry_you_description))

    frame_buttons = tk.Frame(popup_window, bg=FRAME_BG)
    frame_buttons.grid(row=2, column=0, sticky="EW", pady=10, padx=10)
    frame_buttons.columnconfigure(0, weight=1)
    popup_add_button = tk.Button(frame_buttons, text='Add', width=15, bg=BUTTON_BG, fg=BUTTON_FG)
    popup_add_button.grid(row=0, column=1, sticky="w")
    popup_cancel_button = tk.Button(frame_buttons, text="Cancel", command=lambda: popup_window.destroy(), width=15, bg=BUTTON_BG, fg=BUTTON_FG)
    popup_cancel_button.grid(row=0, column=2, sticky="w")

    if len(d) != 0:
        entry_your_name.delete(0, 'end')
        entry_your_name.insert(0, my_data[0])
        text_year_start.delete(0, 'end')
        text_year_start.insert(0, my_data[1].year)
        text_month_start.delete(0, 'end')
        text_month_start.insert(0, my_data[1].month)
        text_day_start.delete(0, 'end')
        text_day_start.insert(0, my_data[1].day)
        entry_you_description.delete(0, 'end')
        entry_you_description.insert(0, my_data[2])
        popup_add_button.configure(text='Update')
    else:
        entry_your_name.delete(0, 'end')
        entry_your_name.insert(0, my_data[0])
        text_year_start.delete(0, 'end')
        text_year_start.insert(0, my_data[1][0])
        text_month_start.delete(0, 'end')
        text_month_start.insert(0, my_data[1][1])
        text_day_start.delete(0, 'end')
        text_day_start.insert(0, my_data[1][2])
        entry_you_description.delete(0, 'end')
        entry_you_description.insert(0, my_data[2])
        popup_add_button.configure(text='Update')


class FrameSettings(tk.Frame):

    def __init__(self, container):
        super().__init__(container)
        self.columnconfigure(0, weight=1)
        self.configure(bg=FRAME_BG)
        self.grid(row=1, column=0, sticky='news')
        font_settings_label = font.Font(family="Carlito", size=14, weight="bold")
        tk.Label(self, text="System", bg=LABEL_BG, fg=LABEL_FG, font=font_settings_label).grid(row=0, column=0, sticky='ew', pady=(10, 0))
        tk.Button(self, text="My birthday", bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: my_birthday_window()).grid(row=1, column=0, sticky="ew", pady=(10, 0))
        expired_events_button = tk.Button(self, text="Expired Events", bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: expired_events_window(expired_events_button))
        expired_events_button.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        lg.unbind_everything(root)
        ev = db.get_all_items('events')
        no_expired = 0
        for e in ev:
            if lg.strtodate(e[1]) < lg.today:
                no_expired += 1
        if no_expired == 0:
            expired_events_button.configure(fg='grey', command=lambda: statusbar.set("No expired events"), text="Expired Events (0)")
        else:
            expired_events_button.configure(text=f"Expired Events ({no_expired})", bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: expired_events_window(expired_events_button))
        ttk.Separator(self).grid(row=5, column=0, sticky='ew', pady=(10, 0))
        tk.Label(self, text="Database", bg=LABEL_BG, fg=LABEL_FG, font=font_settings_label).grid(row=6, column=0, sticky='ew', pady=(10, 0))
        tk.Button(self, text="Database settings", bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: (db.DatabaseManager(root, cm=lambda: start_app()).grid(row=1, column=0, sticky='news'))).grid(row=4, column=0, sticky="ew", pady=(10, 0))
        tk.Button(self, text="Export", bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: (db.database_backup())).grid(row=8, column=0, sticky="ew", pady=(10, 0))
        tk.Button(self, text="Export Anniversaries and Events to JSON", bg=BUTTON_BG, fg=BUTTON_FG, command=lambda: lg.json_export()).grid(row=9, column=0, sticky="ew", pady=(10, 0))
        ttk.Separator(self).grid(row=10, column=0, sticky='ew', pady=(10, 0))
        statusbar.set("SETTINGS")


class FrameDates(tk.Frame):

    def __init__(self, container, data=None, which_table=''):
        super().__init__(container)
        self.grid(row=1, column=0, sticky="news")
        self.data = data
        self.which_table = which_table
        self.configure(bg=FRAME_BG)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.button_add_new = tk.Button(self, text=f"Add new", bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", activebackground=BUTTON_BG, activeforeground=BUTTON_FG, width=30)
        self.button_add_new.grid(row=2, column=0, sticky="ew", pady=(2, 0))
        if self.which_table == 'dates':
            self.button_add_new['command'] = lambda: FrameAddUpdate(root, which_table="dates")
        elif self.which_table == 'anniversaries':
            self.button_add_new['command'] = lambda: FrameAddUpdate(root, which_table="anniversaries")
        elif self.which_table == 'events':
            self.button_add_new['command'] = lambda: FrameAddUpdate(root, which_table="events")
        dates_as_anniversaries = []
        if self.which_table == 'anniversaries':
            dates_as_anniversaries = db.get_dates_as_anniversaries()
        lg.unbind_everything(root)
        if data:
            lst = []
            expired_events = []
            for i in data:
                i_as_date = lg.strtodate(i[1])
                date_to_append = i_as_date
                if self.which_table == "anniversaries":
                    new_date = lg.add_year_if_anniversary_in_the_past(i_as_date)
                    lst.append([i[-1], i[0], new_date, i[2], i[3]])
                    lst.sort(key=lambda x: x[2])
                elif self.which_table == "events":
                    if date_to_append >= lg.today:
                        lst.append([i[-1], i[0], date_to_append, i[2], i[3]])
                        lst.sort(key=lambda x: x[2])
                    else:
                        expired_events.append([i[-1], i[0], date_to_append, i[2], i[3]])
                        expired_events.sort(key=lambda x: x[2])
                elif self.which_table == 'dates':
                    lst.append([i[-1], i[0], date_to_append, i[2], i[3], i[4], i[5]])
                    lst.sort(key=lambda x: x[2], reverse=True)
            if self.which_table == "anniversaries":
                for da in dates_as_anniversaries:
                    da_i_as_date = lg.strtodate(da[1])
                    da_new_date = lg.add_year_if_anniversary_in_the_past(da_i_as_date)
                    lst.append([da[-1], da[0], da_new_date, da[2], da[3]])
                lst.sort(key=lambda x: x[2])
            self.scroll_area = Limiter(self, data=lst, which_table=self.which_table, widgets_per_window=8)
            self.scroll_area.grid(row=0, column=0, sticky="news")
            self.scroll_area.columnconfigure(0, weight=1)


class FrameDurations(tk.Frame):
    def __init__(self, container, data=None):
        super().__init__(container)
        self.grid(row=1, column=0, sticky="news")
        self.data = data
        self.data.sort(key=lambda x: lg.strtodate(x[1][1]) - lg.strtodate(x[0][1]))
        self.configure(bg=FRAME_BG)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        statusbar.set("DURATIONS")
        lg.unbind_everything(root)
        Limiter(self, data=data, which_table='durations', widgets_per_window=13).grid(row=0, column=0, sticky="news")


class FramePersonalDiary(tk.Frame):
    def __init__(self, container, data=None):
        super().__init__(container)
        self.grid(row=1, column=0, sticky="news")
        self.data = data
        self.configure(bg=FRAME_BG)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.font_number_of_days = font.Font(family="Segoe Print", size=16, weight="bold")
        self.font_details = font.Font(family="Segoe Print", size=12)
        self.button_add_new = tk.Button(self, text=f"Add new", bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", activebackground=BUTTON_BG, activeforeground=BUTTON_FG, width=30)
        self.button_add_new.grid(row=2, column=0, sticky="ew")
        self.button_add_new['command'] = lambda: FrameAddUpdateDiary(root)
        lg.unbind_everything(root)
        lst = []
        for i in self.data:
            start_as_date = lg.strtodate(i[1])
            if i[3]:
                end_as_date = lg.strtodate(i[3])
            else:
                end_as_date = None
            lst.append([i[0], start_as_date, i[2], end_as_date, i[4], i[5], i[6]])
            lst.sort(key=lambda x: x[1], reverse=True)

        self.scroll_area = Limiter(self, data=lst, which_table='diary', widgets_per_window=8)
        self.scroll_area.grid(row=0, column=0, sticky="news")
        self.scroll_area.columnconfigure(0, weight=1)


class FrameAddUpdateDiary(tk.Frame):
    def __init__(self, container, data=None, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.data = data
        self.grid(row=1, column=0, sticky="news")
        self.columnconfigure((0, 2), weight=1)
        self.rowconfigure((0, 2), weight=1)
        self.configure(bg=FRAME_BG)
        lg.unbind_everything(root)
        self.middle_frame = tk.Frame(self, bg=FRAME_BG, pady=20, padx=20)
        self.middle_frame.grid(row=1, column=1, sticky="news")
        self.buttons_frame = tk.Frame(self.middle_frame, bg=FRAME_BG)
        if self.data:
            self.data_formatted = self.data.copy()
            self.data_formatted[1] = [str(self.data[1].year), str(self.data[1].month), str(self.data[1].day)]
            if self.data[3]:
                self.data_formatted[3] = [str(self.data[3].year), str(self.data[3].month), str(self.data[3].day)]
            else:
                self.data_formatted[3] = None
            self.op_option = "Update"
            self.insert_font_colour = "black"
            self.button_delete = tk.Button(self.buttons_frame, text="DELETE", bg="#C21010", fg="white", relief="flat", width=15, activebackground=BUTTON_BG, activeforeground=BUTTON_FG)
            self.button_delete.grid(row=0, column=0, sticky="e")
            self.button_delete['command'] = lambda: self.delete_date()
        else:
            self.data_formatted = ['Title', ['yyyy', 'mm', 'dd'], 'Start note', ['yyyy', 'mm', 'dd'], 'End note', 'Description', None]
            self.op_option = "Add"
            self.insert_font_colour = "grey"

        tk.Label(self.middle_frame, text=f"Add diary event", font=("Calibri", 24), bg=LABEL_BG, fg=LABEL_FG).grid(row=0, column=0, sticky="EW", pady=(0, 20))

        self.date_frame = tk.Frame(self.middle_frame, bg=FRAME_BG)
        self.date_frame.grid(row=1, column=0, pady=(0, 10))

        tk.Label(self.date_frame, text="Date: ", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=1, column=0)

        self.text_year_start = tk.Entry(self.date_frame, width=6, font=("Times", 12, "italic"), fg=self.insert_font_colour)
        self.text_year_start.grid(row=1, column=1)
        self.text_year_start.insert(0, self.data_formatted[1][0])
        tk.Label(self.date_frame, text="-", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=1, column=2)

        self.text_month_start = tk.Entry(self.date_frame, width=4, font=("Times", 12, "italic"), fg=self.insert_font_colour)
        self.text_month_start.insert(0, self.data_formatted[1][1])
        self.text_month_start.grid(row=1, column=3)

        tk.Label(self.date_frame, text="-", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=1, column=4)
        self.text_day_start = tk.Entry(self.date_frame, width=4, font=("Times", 12, "italic"), fg=self.insert_font_colour)
        self.text_day_start.insert(0, self.data_formatted[1][2])
        self.text_day_start.grid(row=1, column=5)

        tk.Label(self.date_frame, text="Date end: ", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=2, column=0)
        self.text_year_end = tk.Entry(self.date_frame, width=6, font=("Times", 12, "italic"), fg=self.insert_font_colour)
        self.text_year_end.grid(row=2, column=1)

        tk.Label(self.date_frame, text="-", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=2, column=2)
        self.text_month_end = tk.Entry(self.date_frame, width=4, font=("Times", 12, "italic"), fg=self.insert_font_colour)
        self.text_month_end.grid(row=2, column=3)

        tk.Label(self.date_frame, text="-", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=2, column=4)
        self.text_day_end = tk.Entry(self.date_frame, width=4, font=("Times", 12, "italic"), fg=self.insert_font_colour)
        self.text_day_end.grid(row=2, column=5)
        if self.data_formatted[3]:
            self.text_year_end.insert(0, self.data_formatted[3][0])
            self.text_month_end.insert(0, self.data_formatted[3][1])
            self.text_day_end.insert(0, self.data_formatted[3][2])
        else:
            self.text_year_end.insert(0, "yyyy")
            self.text_month_end.insert(0, "mm")
            self.text_day_end.insert(0, "dd")

        self.text_title = tk.Entry(self.middle_frame, width=40, fg=self.insert_font_colour, font=("Times", 14))
        self.text_title.grid(row=2, column=0, sticky="ew")
        self.text_title.insert(0, self.data_formatted[0])

        self.text_start_note = tk.Entry(self.middle_frame, width=40, fg=self.insert_font_colour, font=("Times", 14))
        self.text_start_note.grid(row=3, column=0, sticky="ew")
        self.text_start_note.insert(0, self.data_formatted[2])

        self.text_end_note = tk.Entry(self.middle_frame, width=40, fg=self.insert_font_colour, font=("Times", 14))
        self.text_end_note.grid(row=4, column=0, sticky="ew")
        self.text_end_note.insert(0, self.data_formatted[4])

        self.text_description = tk.Text(self.middle_frame, fg=self.insert_font_colour, height=7, font=("Times", 10), width=20)
        self.text_description.grid(row=5, column=0, sticky="ew")
        self.text_description.insert("1.0", self.data_formatted[5])

        if not self.data:
            self.text_year_start.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_year_start))
            self.text_year_start.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_year_start))
            self.text_month_start.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_month_start))
            self.text_month_start.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_month_start))
            self.text_day_start.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_day_start))
            self.text_day_start.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_day_start))

            self.text_year_end.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_year_end))
            self.text_year_end.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_year_end))
            self.text_month_end.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_month_end))
            self.text_month_end.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_month_end))
            self.text_day_end.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_day_end))
            self.text_day_end.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_day_end))

            self.text_title.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_title))
            self.text_title.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_title))

            self.text_start_note.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_start_note))
            self.text_start_note.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_start_note))

            self.text_end_note.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_end_note))
            self.text_end_note.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_end_note))

            self.text_description.bind("<Button-1>", lambda event: [self.text_description.delete("1.0", "end-1c"), self.text_description.unbind("<Button-1>"), self.text_description.unbind("<FocusIn>")])
            self.text_description.bind("<FocusIn>", lambda event: [self.text_description.delete("1.0", "end-1c"), self.text_description.unbind("<Button-1>"), self.text_description.unbind("<FocusIn>")])

        self.buttons_frame.grid(row=12, column=0, pady=(10, 0))
        self.button_ok = tk.Button(self.buttons_frame, text=self.op_option, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", width=15, activebackground=BUTTON_BG, activeforeground=BUTTON_FG)
        self.button_ok['command'] = lambda: self.check_data_and_apply()
        self.button_ok.grid(row=0, column=1, sticky="e", padx=10)

        self.button_cancel = tk.Button(self.buttons_frame, text="Cancel", bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", width=15, activebackground=BUTTON_BG, activeforeground=BUTTON_FG)
        self.button_cancel.grid(row=0, column=2, sticky="e")
        self.button_cancel['command'] = lambda: FramePersonalDiary(root, data=db.get_personal_diary_items())

        self.text_day_start.bind("<Return>", lambda event: self.check_data_and_apply())
        self.text_day_end.bind("<Return>", lambda event: self.check_data_and_apply())

        self.text_title.bind("<Return>", lambda event: self.check_data_and_apply())
        self.text_start_note.bind("<Return>", lambda event: self.check_data_and_apply())
        self.text_end_note.bind("<Return>", lambda event: self.check_data_and_apply())

    def check_data_and_apply(self):
        statusbar.set("")
        diary_name = ''
        if len(self.text_title.get()) != 0:
            diary_name = self.text_title.get()
        else:
            statusbar.set("Add title")
        diary_date_start = ''
        y_date = self.text_year_start.get()
        m_date = self.text_month_start.get()
        if len(m_date) == 1:
            m_date = f"0{m_date}"
        d_date = self.text_day_start.get()
        if len(d_date) == 1:
            d_date = f"0{d_date}"
        raw_date_start = f"{y_date}-{m_date}-{d_date}"
        if lg.check_input_date(raw_date_start):
            diary_date_start = raw_date_start
        else:
            statusbar.set("Wrong start date, please try again")
        diary_date_end = ''
        y_date = self.text_year_end.get()
        m_date = self.text_month_end.get()
        if len(m_date) == 1:
            m_date = f"0{m_date}"
        d_date = self.text_day_end.get()
        if len(d_date) == 1:
            d_date = f"0{d_date}"
        raw_date_end = f"{y_date}-{m_date}-{d_date}"
        if lg.check_input_date(raw_date_end):
            diary_date_end = raw_date_end
        else:
            statusbar.set("Wrong end date, please try again")

        diary_date_start_title = self.text_start_note.get()
        diary_date_end_title = self.text_end_note.get()

        diary_description = self.text_description.get("1.0", "end-1c")

        diary_id = self.data_formatted[-1]

        if diary_name and diary_date_start:
            if self.op_option == "Update":
                db.personal_diary_update_item(diary_name=diary_name, diary_date_start=diary_date_start, diary_date_start_title=diary_date_start_title, diary_date_end=diary_date_end, diary_date_end_title=diary_date_end_title, diary_description=diary_description, diary_id=diary_id)
            else:
                db.personal_diary_add_item(diary_name=diary_name, diary_date_start=diary_date_start, diary_date_start_title=diary_date_start_title, diary_date_end=diary_date_end, diary_date_end_title=diary_date_end_title, diary_description=diary_description)
            FramePersonalDiary(root, data=db.get_personal_diary_items())

    def delete_date(self):
        if messagebox.askokcancel(title=f"Delete {self.data_formatted[1]}?", message=f"Are you sure you want to delete this entry?\n\n{self.data_formatted[1][0]}{self.data_formatted[1][1]}{self.data_formatted[1][2]} - {self.data_formatted[0]}"):
            db.personal_diary_delete_item(self.data_formatted[-1])
            statusbar.set('Entry deleted')
            FramePersonalDiary(root, data=db.get_personal_diary_items())


class FrameAddUpdate(tk.Frame):
    def __init__(self, container, data=None, which_table='dates', *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.data = data
        self.which_table = which_table
        self.grid(row=1, column=0, sticky="news")
        self.columnconfigure((0, 2), weight=1)
        self.rowconfigure((0, 2), weight=1)
        self.configure(bg=FRAME_BG)
        lg.unbind_everything(root)
        self.middle_frame = tk.Frame(self, bg=FRAME_BG, pady=20, padx=20)
        self.middle_frame.grid(row=1, column=1, sticky="news")
        self.buttons_frame = tk.Frame(self.middle_frame, bg=FRAME_BG)

        if self.data:
            self.data_formatted = self.data.copy()
            self.data_formatted[2] = [str(self.data[2].year), str(self.data[2].month), str(self.data[2].day)]
            self.op_option = "Update"
            self.insert_font_colour = "black"
            self.button_delete = tk.Button(self.buttons_frame, text="DELETE", bg="#C21010", fg="white", relief="flat", width=15, activebackground=BUTTON_BG, activeforeground=BUTTON_FG)
            self.button_delete.grid(row=0, column=0, sticky="e")
            self.button_delete['command'] = lambda: self.delete_date()
        else:
            self.data_formatted = ['ID', 'Title', ['yyyy', 'mm', 'dd'], 'Description', 'Select beginning', 'Add to anniversaries', 'Type']
            self.op_option = "Add"
            self.insert_font_colour = "grey"

        tk.Label(self.middle_frame, text=f"{self.op_option} {self.which_table}", font=("Calibri", 24), bg=LABEL_BG, fg=LABEL_FG).grid(row=0, column=0, sticky="EW", pady=(0, 20))

        self.date_frame = tk.Frame(self.middle_frame, bg=FRAME_BG)
        self.date_frame.grid(row=1, column=0, pady=(0, 10))
        tk.Label(self.date_frame, text="Date: ", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=1, column=0)

        self.text_year = tk.Entry(self.date_frame, width=6, font=("Times", 12, "italic"), fg=self.insert_font_colour)
        self.text_year.grid(row=1, column=1)
        self.text_year.insert(0, self.data_formatted[2][0])
        tk.Label(self.date_frame, text="-", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=1, column=2)

        self.text_month = tk.Entry(self.date_frame, width=4, font=("Times", 12, "italic"), fg=self.insert_font_colour)
        self.text_month.insert(0, self.data_formatted[2][1])
        self.text_month.grid(row=1, column=3)

        tk.Label(self.date_frame, text="-", font=("Calibri", 9), bg=LABEL_BG, fg=LABEL_FG).grid(row=1, column=4)
        self.text_day = tk.Entry(self.date_frame, width=4, font=("Times", 12, "italic"), fg=self.insert_font_colour)
        self.text_day.insert(0, self.data_formatted[2][2])
        self.text_day.grid(row=1, column=5)

        self.text_title = tk.Entry(self.middle_frame, width=40, fg=self.insert_font_colour, font=("Times", 14))
        self.text_title.grid(row=4, column=0, sticky="ew")
        self.text_title.insert(0, self.data_formatted[1])

        self.text_description = tk.Text(self.middle_frame, fg=self.insert_font_colour, height=7, font=("Times", 10), width=20)
        self.text_description.grid(row=5, column=0, sticky="ew")
        self.text_description.insert("1.0", self.data_formatted[3])

        if not self.data:
            self.text_year.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_year))
            self.text_year.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_year))
            self.text_month.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_month))
            self.text_month.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_month))
            self.text_day.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_day))
            self.text_day.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_day))
            self.text_title.bind("<Button-1>", lambda event: lg.clear_entry_placeholders(self.text_title))
            self.text_title.bind("<FocusIn>", lambda event: lg.clear_entry_placeholders(self.text_title))
            self.text_description.bind("<Button-1>", lambda event: [self.text_description.delete("1.0", "end-1c"), self.text_description.unbind("<Button-1>"), self.text_description.unbind("<FocusIn>")])
            self.text_description.bind("<FocusIn>", lambda event: [self.text_description.delete("1.0", "end-1c"), self.text_description.unbind("<Button-1>"), self.text_description.unbind("<FocusIn>")])

        if self.which_table == 'dates':
            self.checkbutton = tk.StringVar()
            ttk.Checkbutton(self.middle_frame, text='Display with anniversaries', variable=self.checkbutton, onvalue=1, offvalue=0).grid(row=6, column=0, sticky='news')

            if self.op_option == "Update":
                self.checkbutton.set(self.data[-2])
                tk.Label(self.middle_frame, text="Select beginning to add entry to Durations", bg=LABEL_BG, fg=LABEL_FG).grid(row=7, column=0, sticky='ew', pady=(10, 5))

                self.combobox = ttk.Combobox(self.middle_frame, state="readonly")
                self.combobox.set("")
                self.combobox_data_raw = db.get_all_items(table_name='dates')
                self.combobox_data = [[]]
                for c_d in self.combobox_data_raw:
                    if c_d[-1] != self.data_formatted[0] and c_d[1] < self.data[2].strftime("%Y-%m-%d"):
                        self.combobox_data.append(f"{c_d[0]} - {c_d[1]}")
                self.combobox['values'] = self.combobox_data
                if self.data[-3]:
                    with sqlite3.connect(database_name) as connection:
                        cursor = connection.cursor()
                        combobox_insert_data = cursor.execute(f"SELECT * FROM dates WHERE rowid={self.data[-3]}").fetchall()
                        cursor.close()
                    c_text = f"{combobox_insert_data[0][0]} - {combobox_insert_data[0][1]}"
                    self.combobox.current(self.combobox_data.index(c_text))
                self.combobox.grid(row=8, column=0, sticky='news')

        self.buttons_frame.grid(row=12, column=0, pady=(10, 0))
        self.button_ok = tk.Button(self.buttons_frame, text=self.op_option, bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", width=15, activebackground=BUTTON_BG, activeforeground=BUTTON_FG)
        self.button_ok['command'] = lambda: self.check_data_and_apply()
        self.button_ok.grid(row=0, column=1, sticky="e", padx=10)

        self.button_cancel = tk.Button(self.buttons_frame, text="Cancel", bg=BUTTON_BG, fg=BUTTON_FG, relief="flat", width=15, activebackground=BUTTON_BG, activeforeground=BUTTON_FG)
        self.button_cancel.grid(row=0, column=2, sticky="e")
        self.button_cancel['command'] = lambda: FrameDates(root, db.get_all_items(self.which_table), which_table=self.which_table)

        self.text_day.bind("<Return>", lambda event: self.check_data_and_apply())
        self.text_title.bind("<Return>", lambda event: self.check_data_and_apply())

    def check_data_and_apply(self):
        statusbar.set("")
        t_name = ''
        if len(self.text_title.get()) != 0:
            t_name = self.text_title.get()
        else:
            statusbar.set("Add title")
        t_date = ''
        y_date = self.text_year.get()
        m_date = self.text_month.get()
        if len(m_date) == 1:
            m_date = f"0{m_date}"
        d_date = self.text_day.get()
        if len(d_date) == 1:
            d_date = f"0{d_date}"
        raw_date = f"{y_date}-{m_date}-{d_date}"
        if lg.check_input_date(raw_date):
            t_date = raw_date
        else:
            statusbar.set("Wrong date, please try again")
        t_description = self.text_description.get("1.0", "end-1c")
        t_type = self.which_table
        t_id = self.data_formatted[0]
        t_anniversaries = 0
        t_id_beginning = None

        if t_date and t_name:
            if self.which_table == 'dates':
                t_anniversaries = self.checkbutton.get()
                if self.op_option == "Update":
                    combobox_selection = self.combobox.current()
                    if combobox_selection != 0:
                        list_of_dates_index = combobox_selection - 1
                        entry_index_in_list = self.combobox_data_raw[list_of_dates_index]
                        entry_actual_index_to_add_as_beginning = entry_index_in_list[-1]
                        t_id_beginning = entry_actual_index_to_add_as_beginning
                    db.tables_update_item(self.which_table, t_name=t_name, t_date=t_date, t_description=t_description, t_id_beginning=t_id_beginning, t_anniversaries=t_anniversaries, t_type=t_type, t_id=t_id)
                else:
                    db.tables_add_item(self.which_table, t_name=t_name, t_date=t_date, t_description=t_description, t_id_beginning=t_id_beginning, t_anniversaries=t_anniversaries, t_type=t_type)
            else:
                if self.op_option == "Update":
                    db.tables_update_item(self.which_table, t_name=t_name, t_date=t_date, t_description=t_description, t_id_beginning=t_id_beginning, t_anniversaries=t_anniversaries, t_type=t_type, t_id=t_id)
                else:
                    db.tables_add_item(self.which_table, t_name=t_name, t_date=t_date, t_description=t_description, t_id_beginning=t_id_beginning, t_anniversaries=t_anniversaries, t_type=t_type)
            FrameDates(root, data=db.get_all_items(self.which_table), which_table=self.which_table)

    def delete_date(self):
        if messagebox.askokcancel(title=f"Delete {self.data_formatted[1]}?", message=f"Are you sure you want to delete this entry?\n\n{self.data_formatted[2][0]}{self.data_formatted[2][1]}{self.data_formatted[2][2]} - {self.data_formatted[1]}"):
            if self.which_table == 'dates':
                db.table_dates_delete_item_and_set_foreign_keys_to_null(self.data_formatted[0])
            else:
                db.tables_delete_item(self.which_table, self.data_formatted[0])
            statusbar.set('Entry deleted')
            FrameDates(root, data=db.get_all_items(self.which_table), which_table=self.which_table)


def start_app():
    try:
        db.get_all_items('anniversaries')
        FrameMenu(root)
        FrameHome(root)
        label_statusbar = tk.Label(root, textvariable=statusbar, bg="#222831", fg="white", pady=10)
        label_statusbar.grid(row=2, column=0, sticky="ew", pady=(2, 0))
    except sqlite3.OperationalError:
        db.DatabaseManager(root, cm=lambda: start_app()).grid(rowspan=3)


root = tk.Tk()
root.geometry("1000x1700+200+200")
root.title("Events")
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.resizable(False, False)
root.configure(bg=FRAME_BG)
statusbar = tk.StringVar()

font_home_week = font.Font(family="Ink Free", size=24)
font_home_date = font.Font(family="Ink Free", size=50)
font_number_of_days = font.Font(family="Segoe Print", size=16, weight="bold")
font_date_details = font.Font(family="Merriweather", size=8)
font_menu_buttons = font.Font(family="Carlito", size=10, weight="bold")
font_event_name = font.Font(family="Merriweather", size=12)


start_app()

root.mainloop()
