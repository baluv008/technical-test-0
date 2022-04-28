import sqlite3
import os
import time
import pandas as pd


class TimeLogger:
    """
    Class
    """
    def __init__(self, emp_id=None):
        """
        Constructor
        :param emp_id:
        :return:
        """
        self.__connection__ = None
        self.__cursor__ = None
        self.__connect_db__()
        self.__employee_id__ = emp_id
        if self.__employee_id__ is None:
            self.change_employee_id()

    def __connect_db__(self):
        """
        Method to create db connection and db cursor
        :param:
        :return:
        """
        db_exist = True
        if not os.path.exists("Db_time-logger.sqlite"):
            db_exist = False
        self.__connection__ = sqlite3.connect("Db_time-logger.sqlite")
        self.__cursor__ = self.__connection__.cursor()
        if not db_exist:
            self.__create_tables__()

    def __create_tables__(self):
        """
        Method creates table.
        :param:
        :return:
        """
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
        """
        Method to execute a query,  DB changes will be commited based on the `db_commit` parameter.
        :param query: SQL query to be executed
        :param do_commit:
        :return:
        """
        self.__cursor__.execute(query)
        if do_commit:
            self.__connection__.commit()

    def change_employee_id(self):
        """
        Method to change the employee ID.
        :param:
        :return:
        """
        employee_id = input("Enter employee ID: ")
        self.__employee_id__ = employee_id

    def __check_last_entry(self):
        """
        Method to fetch the last entry.
        :param:
        :return:
        """
        check_query = "SELECT max(entry_id),start_time,end_time from T_time_logger where employee_id='%s'" % (
            self.__employee_id__)
        self.__run_query__(check_query)
        data = self.__cursor__.fetchone()
        return data

    def start_timer(self):
        """
        Method to start the timer.
        :param:
        :return:
        """
        insert_query = "INSERT INTO T_time_logger(employee_id,start_date,start_time,description) VALUES"
        latest_entry = self.__check_last_entry()

        if latest_entry[0] is None or latest_entry[2] is not None: #Check if the timer is stopped in the last entry or if its the first entry
            entry_date = time.strftime("%Y-%m-%d") #Entry date set to current date
            entry_time = time.strftime("%H:%M") #Entry date set to current time
            description = input("Enter description: ") #Reads the description/message from user
            insert_query = insert_query + "('%s','%s','%s','%s')" % (
                self.__employee_id__, entry_date, entry_time, description)
            self.__run_query__(insert_query, do_commit=True)
            print("Timer Started...\n")

        else:
            #If this is not th first entry or if the previous timer is  not stopped then inform the user
            confirmation = input(
                "Unable to Start timer. Do you want to stop the running timer and start a new one?(Y/N)")
            if confirmation.lower() == "y":
                self.stop_timer()
                self.start_timer()

    def stop_timer(self):
        """
        Method to stop the timer.
        :param:
        :return:
        """
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
        """
        Method to update the description/message
        :param:
        :return:
        """

        df = self.list_all_entries(filter_emp=True)

        if df.count()["entry_id"] != 0:
            entry_id = input("\nEnter the entry_id for which you want to update the description: ")
            if int(entry_id) in list(df['entry_id']):
                desc = input("Enter description: ")
                update_query = "UPDATE T_time_logger set description = '%s' where entry_id = %s" % (desc, entry_id)
                self.__run_query__(update_query, do_commit=True)
                print("Entry Updated...\n")
            else:
                input("Invalid entry_id!\n")

    def delete_entry(self):
        """
        Method to Delete an entry
        :return:
        """
        df= self.list_all_entries(True)
        if df.count()["entry_id"] != 0:
            entry_id = input("\nEnter the entry_id to be deleted: ") #Entry ID to be deleted
            if int(entry_id) in list(df['entry_id']):
                delete_query = "DELETE from T_time_logger where entry_id = %s" % entry_id
                self.__run_query__(delete_query, do_commit=True)
                print("Entry Deleted...\n")
            else:
                print("Invalid entry_id!\n")


    def list_all_entries(self, filter_emp=False):
        """
        Method to list all entries
        :param filter_emp: Boolean paramaneter. IF set to try then filter using employee_id
        :return df: Pandas dataframe
        """
        select_query = "SELECT entry_id, employee_id, start_date, start_time, end_date, end_time, description from " \
                       "T_time_logger "
        if filter_emp:
            select_query += "WHERE employee_id=%s"% self.__employee_id__

        df = pd.read_sql_query(select_query, self.__connection__)

        if df.count()["entry_id"] != 0:
            print(df.to_string(index=False))
            print("\n")
        else:
            print("No entries in DB!!\n")
        return df


def invalid_selection():
    print("Invalid input given!!!\n\n")


if __name__ == "__main__":
    timerObj = TimeLogger(1)
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
