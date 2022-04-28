import sqlite3
import os
import time
import pandas as pd


class TimeLogger:

    def __init__(self, emp_id=None):
        self.__connection__ = None
        self.__cursor__ = None
        self.__connect_db__()
        self.__employee_id__ = emp_id
        if self.__employee_id__ is None:
            self.change_employee_id()

    def __connect_db__(self):
        db_exist = True
        if not os.path.exists("Db_time-logger.sqlite"):
            db_exist = False
        self.__connection__ = sqlite3.connect("Db_time-logger.sqlite")
        self.__cursor__ = self.__connection__.cursor()
        if not db_exist:
            self.__create_tables__()

    def __create_tables__(self):
        create_query = 'CREATE TABLE "T_time_logger" \
        ("entry_id"	INTEGER NOT NULL,\
        "employee_id"	TEXT NOT NULL,\
        "start_date"	TEXT NOT NULL,\
        "start_time"	TEXT NOT NULL,\
        "end_date"	TEXT,\
        "end_time"	TEXT,\
        "description"   TEXT,\
        PRIMARY KEY("entry_id" AUTOINCREMENT) );'
        self.__cursor__.execute(create_query)
        self.__connection__.commit()

    def __run_query__(self, query, do_commit=False):
        self.__cursor__.execute(query)
        if do_commit:
            self.__connection__.commit()

    def change_employee_id(self):
        employee_id = input("Enter employee ID: ")
        self.__employee_id__ = employee_id

    def __check_last_entry(self):
        check_query = "SELECT max(entry_id),start_time,end_time from T_time_logger where employee_id='%s'" % (
            self.__employee_id__)
        self.__run_query__(check_query)
        data = self.__cursor__.fetchone()
        return data

    def start_timer(self):
        insert_query = "INSERT INTO T_time_logger(employee_id,start_date,start_time,description) VALUES"
        latest_entry = self.__check_last_entry()

        if latest_entry[0] is None or latest_entry[2] is not None:
            entry_date = time.strftime("%Y-%m-%d")
            entry_time = time.strftime("%H:%M")
            entry_type = "start"
            description = input("Enter description: ")
            insert_query = insert_query + "('%s','%s','%s','%s')" % (
                self.__employee_id__, entry_date, entry_time, description)
            self.__run_query__(insert_query, do_commit=True)
            print("Timer Started...\n")

        else:
            confirmation = input(
                "Unable to Start timer. Do you want to stop the running timer and start a new one?(Y/N)")
            if confirmation.lower() == "y":
                self.stop_timer()
                self.start_timer()

    def stop_timer(self):

        latest_entry = self.__check_last_entry()
        if latest_entry[2] is None:
            entry_id = latest_entry[0]
            entry_date = time.strftime("%Y-%m-%d")
            entry_time = time.strftime("%H:%M")
            update_query = "UPDATE T_time_logger set end_date='%s', end_time = '%s' where entry_id = %s" % (
                entry_date, entry_time, entry_id)
            self.__run_query__(update_query, do_commit=True)
            print("Timer Stopped...\n")
        else:
            confirmation = input("Unable to Stop timer. Do you want to start and stop now?(Y/N)")
            if confirmation.lower() == "y":
                self.start_timer()
                self.stop_timer()

    def update_message(self):
        select_query = "SELECT entry_id, employee_id, start_date, start_time, end_date, end_time, description \
        from T_time_logger where employee_id='%s'" % self.__employee_id__

        df = pd.read_sql_query(select_query, self.__connection__)

        if df.count()["entry_id"] != 0:
            print(df.to_string(index=False))
            entry_id = input("\nEnter the entry_id for which you want to update the description: ")
            if int(entry_id) in list(df['entry_id']):
                desc = input("Enter description: ")
                update_query = "UPDATE T_time_logger set description = '%s' where entry_id = %s" % (desc, entry_id)
                self.__run_query__(update_query, do_commit=True)
                print("Entry Updated...\n")
            else:
                input("Invalid entry_id!\n")

        else:
            input("No data found!!\n")

    def delete_entry(self):
        select_query = "SELECT entry_id, employee_id, start_date, start_time, end_date, end_time, description \
        from T_time_logger where employee_id='%s'" % self.__employee_id__

        df = pd.read_sql_query(select_query, self.__connection__)

        if df.count()["entry_id"] != 0:
            print(df.to_string(index=False))
            entry_id = input("\nEnter the entry_id to be deleted: ")
            if int(entry_id) in list(df['entry_id']):
                desc = input("Enter description: ")
                delete_query = "DELETE from T_time_logger where entry_id = %s" % (desc, entry_id)
                self.__run_query__(delete_query, do_commit=True)
                print("Entry Deleted...\n")
            else:
                print("Invalid entry_id!\n")

        else:
            print("No data found!!\n")

    def list_all_entries(self):
        select_query = "SELECT entry_id, employee_id, start_date, start_time, end_date, end_time, description from " \
                       "T_time_logger "
        df = pd.read_sql_query(select_query, self.__connection__)

        if df.count()["entry_id"] != 0:
            print(df.to_string(index=False))
            print("\n")


def invalid_selection():
    print("Invalid input given!!!\n\n")


if __name__ == "__main__":
    timerObj = TimeLogger()
    options = {"1": timerObj.start_timer, "2": timerObj.stop_timer, "3": timerObj.update_message,
               "4": timerObj.delete_entry, "5": timerObj.list_all_entries, "6":timerObj.change_employee_id}

    while(True):
        print("Available Options\n-------------------\n")
        print("1. Start Timer")
        print("2. Stop Timer")
        print("3. Update message")
        print("4. Delete entry")
        print("5. List all entries")
        print("6. Change Employee ID\n")
        option = input("Select an Option from the above list or or enter Q to Quit: ")
        if option.lower() != "q":
            run_function = options.get(option, invalid_selection)
            run_function()
        else:
            print("Terminating Program execution..")
            exit(0)
