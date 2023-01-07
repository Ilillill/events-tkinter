import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import pickle
import sqlite3
import shutil
import datetime

database_id = 'events'

try:
    with open("./databases/database_data.dat", "rb") as file:
        database_name = pickle.load(file)
except:
    database_name = ''


def check_database_id(selected_database):
    connection = sqlite3.connect(selected_database)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM database_id")
    check_id = cursor.fetchone()
    cursor.close()
    connection.close()
    if check_id[0] == database_id:
        return True


def database_backup():
    database_path = filedialog.askopenfilename(title="Select database to export", defaultextension="db", initialdir="./databases")
    if database_path:
        path = filedialog.askdirectory(title='Select folder')
        try:
            shutil.copyfile(database_path, f"{path}/{datetime.datetime.now().strftime('%Y%m%d')}_database_backup.db")
        except FileNotFoundError:
            pass


class DatabaseManager(tk.Frame):
    def __init__(self, container, cm=None, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.cm = cm

        self.columnconfigure(0, minsize=500, weight=1)
        self.rowconfigure((0, 1), weight=1)
        self.config(bg='white')
        self.grid(row=0, column=0, sticky='NEWS')

        self.sqlite_logo = tk.PhotoImage(file="./assets_database/logo_sqlite.png")
        self.label_logo_sqlite = tk.Label(self, image=self.sqlite_logo, bg='white', height=304)
        self.label_logo_sqlite.grid(row=0, column=0, sticky='s', padx=50, pady=50)

        self.buttons_frame = tk.Frame(self, bg='white')
        self.buttons_frame.grid(row=1, column=0, sticky='n')
        self.buttons_frame.columnconfigure((0, 1), weight=1)

        self.create_image = tk.PhotoImage(file="./assets_database/database_open.png")
        self.button_sqlite_create = tk.Button(self.buttons_frame, image=self.create_image, compound="top", text="OPEN", width=150, bg='white', relief='flat')
        self.button_sqlite_create["command"] = lambda: self.database_open()
        self.button_sqlite_create.grid(row=0, column=0, sticky="ew")

        self.open_image = tk.PhotoImage(file="./assets_database/database_add.png")
        self.button_sqlite_open = tk.Button(self.buttons_frame, image=self.open_image, compound="top", text="CREATE", width=150, bg='white', relief='flat',)
        self.button_sqlite_open["command"] = lambda: self.database_create()
        self.button_sqlite_open.grid(row=0, column=1, sticky="ew")

        self.status_label_database_name = tk.Label(self.buttons_frame, text='', bg='white', fg="black")
        self.status_label_database_name.grid(row=2, column=0, sticky="WE", columnspan=2)

        if self.cm is not None:
            self.start_app_image = tk.PhotoImage(file="./assets_database/apply.png")
            self.button_start_app = tk.Button(self.buttons_frame, text='Launch app', compound="left", bg='white', relief='flat', image=self.start_app_image, state='disabled')
            self.button_start_app["command"] = self.cm
            self.button_start_app.grid(row=3, column=0, pady=20, sticky="ew", columnspan=2)

        if database_name != '':
            self.status_label_database_name.config(text=f"Selected database: {os.path.basename(database_name)}", fg='#0f80cc')
            self.button_start_app['state'] = 'normal'

    def database_create(self):
        global database_name
        try:
            database_path = filedialog.asksaveasfilename(title="Create Database", initialdir="./databases/", defaultextension="db", filetypes=(("Database files *.db", "*.db"), ("All files", "*.*")))
        except (AttributeError, FileNotFoundError):
            return

        if len(database_path) != 0:
            database_name = database_path
            try:
                with sqlite3.connect(database_path) as connection:
                    cursor = connection.cursor()
                    cursor.execute("CREATE TABLE IF NOT EXISTS database_id(d_id text)")
                    cursor.execute("INSERT INTO database_id VALUES(?)", (database_id,))
                    with open("./databases/database_data.dat", "wb") as dumpfile:
                        pickle.dump(database_name, dumpfile)
                    self.status_label_database_name.config(text=f"Selected database: {os.path.basename(database_name)}", fg='#0f80cc')
                    self.button_start_app['state'] = 'normal'
                    create_important_dates = "CREATE TABLE IF NOT EXISTS dates (t_name TEXT NOT NULL, t_date TEXT NOT NULL, t_description TEXT, t_id_beginning INTEGER, t_anniversaries INTEGER, t_type TEXT NOT NULL)"
                    create_events = "CREATE TABLE IF NOT EXISTS events (t_name TEXT NOT NULL, t_date TEXT NOT NULL, t_description TEXT, t_type TEXT NOT NULL)"
                    create_anniversaries = "CREATE TABLE IF NOT EXISTS anniversaries (t_name TEXT NOT NULL, t_date TEXT NOT NULL, t_description TEXT, t_type TEXT NOT NULL)"

                    create_about_you = "CREATE TABLE IF NOT EXISTS you (t_name TEXT NOT NULL, t_date TEXT NOT NULL, t_description TEXT, t_type TEXT NOT NULL)"
                    create_settings = "CREATE TABLE IF NOT EXISTS s_table (s_name TEXT NOT NULL, s_option INTEGER NOT NULL)"
                    create_personal_diary = "CREATE TABLE IF NOT EXISTS personal_diary (diary_name TEXT NOT NULL, diary_date_start TEXT NOT NULL, diary_date_start_title TEXT, diary_date_end TEXT, diary_date_end_title TEXT, diary_description TEXT)"
                    cursor.execute(create_important_dates)
                    cursor.execute(create_events)
                    cursor.execute(create_anniversaries)

                    cursor.execute(create_about_you)
                    cursor.execute(create_settings)
                    cursor.execute(create_personal_diary)
                    cursor.close()
                    connection.commit()
            except sqlite3.Error as error:
                messagebox.showerror(title='Database Error', message=f"{os.path.basename(database_name).capitalize()} ERROR:\n{error}")

    def database_open(self):
        global database_name
        try:
            database_to_import = filedialog.askopenfilename(title="Select database file to open", filetypes=(("Database files", "*.db"), ("All files", "*.*")))
        except (AttributeError, FileNotFoundError):
            messagebox.showinfo(title='Error', message="Error opening database, please try again.")
            return
        if len(database_to_import) != 0:
            if database_to_import != '':
                if check_database_id(database_to_import):
                    database_name = database_to_import
                    with open("./databases/database_data.dat", "wb") as dumpfile:
                        pickle.dump(database_name, dumpfile)
                    self.status_label_database_name.config(text=f"Selected database: {os.path.basename(database_name)}", fg='#0f80cc')
                    self.button_start_app['state'] = 'normal'
                else:
                    messagebox.showinfo(title='Database Error', message=f"{os.path.basename(database_to_import).capitalize()} doesn't belong to this app.")


def get_all_items(table_name):
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()
        data = cursor.execute(f"SELECT *, rowid FROM {table_name} ORDER BY t_date").fetchall()
        connection.row_factory = sqlite3.Row
        cursor.close()
    return data


def get_dates_as_anniversaries():
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()
        data = cursor.execute(f"SELECT *, rowid FROM dates WHERE t_anniversaries=1 ORDER BY t_date").fetchall()
        cursor.close()
    return data


def get_personal_diary_items():
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()
        data = cursor.execute(f"SELECT *, rowid FROM personal_diary ORDER BY diary_date_start").fetchall()
        cursor.close()
    return data


def get_durations():
    with sqlite3.connect(database_name) as connection:
        cursor = connection.cursor()
        data = cursor.execute(f"SELECT * FROM dates WHERE t_id_beginning NOT NULL ORDER BY t_date").fetchall()
        duration_pairs = []
        for selected_date in data:
            d_command = f"SELECT *, rowid FROM dates WHERE rowid=?"
            d_value = (selected_date[-3], )
            beginning_date = cursor.execute(d_command, d_value).fetchone()
            duration_pairs.append([beginning_date, selected_date])
        cursor.close()
    return duration_pairs


def tables_add_item(table_name, t_name, t_date, t_description, t_type, t_id_beginning, t_anniversaries):
    try:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            if table_name == 'dates':
                db_command = f"INSERT INTO {table_name} (t_name, t_date, t_description, t_id_beginning, t_anniversaries, t_type) VALUES (?, ?, ?, ?, ?, ?)"
                db_values = (t_name, t_date, t_description, t_id_beginning, t_anniversaries, t_type)
            else:
                db_command = f"INSERT INTO {table_name} (t_name, t_date, t_description, t_type) VALUES (?, ?, ?, ?)"
                db_values = (t_name, t_date, t_description, t_type)
            cursor.execute(db_command, db_values)
            connection.commit()
            cursor.close()
    except sqlite3.Error as error:
        messagebox.showerror(title='Database Error', message=f"{os.path.basename(database_name).capitalize()} ERROR:\n{error}")


def tables_update_item(table_name, t_name, t_date, t_description, t_id_beginning, t_anniversaries, t_type, t_id):
    try:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            if table_name == 'dates':
                db_command = f"UPDATE {table_name} SET t_name=?, t_date=?, t_description=?, t_id_beginning=?, t_anniversaries=?, t_type=? WHERE rowid=?"
                db_values = (t_name, t_date, t_description, t_id_beginning, t_anniversaries, t_type, t_id)
            else:
                db_command = f"UPDATE {table_name} SET t_name=?, t_date=?, t_description=?, t_type=? WHERE rowid=?"
                db_values = (t_name, t_date, t_description, t_type, t_id)
            cursor.execute(db_command, db_values)
            connection.commit()
            cursor.close()
    except sqlite3.Error as error:
        messagebox.showerror(title='Database Error', message=f"{os.path.basename(database_name).capitalize()} ERROR:\n{error}")


def tables_delete_item(table_name, item_id):
    try:
        with sqlite3.connect(database_name) as connection:
            delete_item_command = f"DELETE FROM {table_name} WHERE rowid=?"
            delete_item_value = (item_id,)
            cursor = connection.cursor()
            cursor.execute(delete_item_command, delete_item_value)
            connection.commit()
            cursor.close()
    except sqlite3.Error as error:
        messagebox.showerror(title='Database Error', message=f"{os.path.basename(database_name).capitalize()} ERROR:\n{error}")


def table_dates_delete_item_and_set_foreign_keys_to_null(item_id):
    try:
        with sqlite3.connect(database_name) as connection:
            delete_item_command = f"DELETE FROM dates WHERE rowid=?"
            delete_item_value = (item_id,)
            update_item_command = f"UPDATE dates SET t_id_beginning=? WHERE t_id_beginning=?"
            update_item_value = (None, item_id)
            cursor = connection.cursor()
            cursor.execute(delete_item_command, delete_item_value)
            cursor.execute(update_item_command, update_item_value)
            connection.commit()
            cursor.close()
    except sqlite3.Error as error:
        messagebox.showerror(title='Database Error', message=f"{os.path.basename(database_name).capitalize()} ERROR:\n{error}")


def personal_diary_add_item(diary_name, diary_date_start, diary_date_start_title, diary_date_end, diary_date_end_title, diary_description):
    try:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()
            db_command = f"INSERT INTO personal_diary (diary_name, diary_date_start, diary_date_start_title, diary_date_end, diary_date_end_title, diary_description) VALUES (?, ?, ?, ?, ?, ?)"
            db_values = (diary_name, diary_date_start, diary_date_start_title, diary_date_end, diary_date_end_title, diary_description)
            cursor.execute(db_command, db_values)
            connection.commit()
            cursor.close()
    except sqlite3.Error as error:
        messagebox.showerror(title='Database Error', message=f"{os.path.basename(database_name).capitalize()} ERROR:\n{error}")


def personal_diary_update_item(diary_name, diary_date_start, diary_date_start_title, diary_date_end, diary_date_end_title, diary_description, diary_id):
    try:
        with sqlite3.connect(database_name) as connection:
            cursor = connection.cursor()

            db_command = f"UPDATE personal_diary SET diary_name=?, diary_date_start=?, diary_date_start_title=?, diary_date_end=?, diary_date_end_title=?, diary_description=? WHERE rowid=?"
            db_values = (diary_name, diary_date_start, diary_date_start_title, diary_date_end, diary_date_end_title, diary_description, diary_id)

            cursor.execute(db_command, db_values)
            connection.commit()
            cursor.close()
    except sqlite3.Error as error:
        messagebox.showerror(title='Database Error', message=f"{os.path.basename(database_name).capitalize()} ERROR:\n{error}")


def personal_diary_delete_item(item_id):
    try:
        with sqlite3.connect(database_name) as connection:
            delete_item_command = f"DELETE FROM personal_diary WHERE rowid=?"
            delete_item_value = (item_id,)
            cursor = connection.cursor()
            cursor.execute(delete_item_command, delete_item_value)
            connection.commit()
            cursor.close()
    except sqlite3.Error as error:
        messagebox.showerror(title='Database Error', message=f"{os.path.basename(database_name).capitalize()} ERROR:\n{error}")