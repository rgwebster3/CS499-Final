
#******************************************************************
# Author: Robert Webster
# Program: Authentication class
# Date: 10/03/2021
# 
# Comments: Database connection
#
#******************************************************************

import os
import pyodbc
import sqlite3
import pandas as pd

class DBMakeConnection():

    def make_connection(self):    
        self.__sys_temp_folder = os.environ['TEMP']
        self.__conn = sqlite3.connect(self.__sys_temp_folder + '\cma.db')
        self.__cursor = self.__conn.cursor()

class DBAuthenticate(DBMakeConnection):
    def __init__(self, login_username): 
        
        self.__login_username = login_username

    def authenticate(self):
        super(DBAuthenticate, self).make_connection()
        
        #get pw from sql
        self._DBMakeConnection__cursor.execute("SELECT * FROM tbl_user_list WHERE username = ?", (self.__login_username, ))
        self.__results = self._DBMakeConnection__cursor.fetchone()

        self._DBMakeConnection__cursor.close()
        del self._DBMakeConnection__cursor

        return self.__results

        #clear and close db
        self._DBMakeConnection__cursor.close()
        del self._DBMakeConnection__cursor

        self._DBMakeConnection__conn.close()
        del self._DBMakeConnection__conn

class DBGetAllClients(DBMakeConnection):

    def __init__(self):
        super(DBGetAllClients, self).make_connection()

    def get_all_clients(self):

        self._DBMakeConnection__cursor.execute("SELECT * FROM tbl_client_list")
        df = pd.DataFrame(self._DBMakeConnection__cursor.fetchall())
        self.__results = df.rename({0: 'ID', 1: 'First Name', 2: 'Last Name', 3: 'Service'}, axis=1)

        #self._DBMakeConnection__cursor.close()
        #del self._DBMakeConnection__cursor

        return  self.__results

        #clear and close db
        self._DBMakeConnection__cursor.close()
        del self._DBMakeConnection__cursor

        self._DBMakeConnection__conn.close()
        del self._DBMakeConnection__conn

class DBGetSingleClient(DBMakeConnection):

    def __init__(self, id):
        super(DBGetSingleClient, self).make_connection()

        self.__id = id

    def get_single_client(self):

        self._DBMakeConnection__cursor.execute("SELECT * FROM tbl_client_list WHERE id = ?", (self.__id, ))
        df = pd.DataFrame(self._DBMakeConnection__cursor.fetchall())
        self.__results = df.rename({0: 'ID', 1: 'First Name', 2: 'Last Name', 3: 'Service'}, axis=1)

        #self._DBMakeConnection__cursor.close()
        #del self._DBMakeConnection__cursor

        return  self.__results

        #clear and close db
        self._DBMakeConnection__cursor.close()
        del self._DBMakeConnection__cursor

        self._DBMakeConnection__conn.close()
        del self._DBMakeConnection__conn

class DBAddSingleClient(DBMakeConnection):

    def __init__(self, form_first_name, form_last_name, form_selected_service):
        super(DBAddSingleClient, self).make_connection()

        self.__form_first_name = form_first_name
        self.__form_last_name = form_last_name
        self.__form_selected_service = form_selected_service

    def add_single_client(self):

        with self._DBMakeConnection__conn:
            self._DBMakeConnection__cursor.execute("INSERT INTO tbl_client_list(first_name, last_name, selected_service) \
                VALUES (?, ?, ?)", (self.__form_first_name, self.__form_last_name, self.__form_selected_service))

        #clear and close db
        self._DBMakeConnection__cursor.close()
        del self._DBMakeConnection__cursor

        self._DBMakeConnection__conn.close()
        del self._DBMakeConnection__conn

class DBUpdateSingleClient(DBMakeConnection):

    def __init__(self, id, first_name, last_name, selected_service):
        super(DBUpdateSingleClient, self).make_connection()

        self.__sys_temp_folder = os.environ['TEMP']
        self.__conn = sqlite3.connect(self.__sys_temp_folder + '\cma.db')
        self.__cursor = self.__conn.cursor()

        self.__id = id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__selected_service = selected_service

    def update_single_client(self):

        with self._DBMakeConnection__conn:
            self._DBMakeConnection__cursor.execute("UPDATE tbl_client_list SET first_name = ?, last_name= ?, selected_service = ? WHERE id = ?", \
                (self.__first_name, self.__last_name, self.__selected_service, self.__id ))

        #clear and close db
        self._DBMakeConnection__cursor.close()
        del self._DBMakeConnection__cursor

        self._DBMakeConnection__conn.close()
        del self._DBMakeConnection__conn

class DBDeleteSingleClient(DBMakeConnection):

    def __init__(self, client_id):
        super(DBDeleteSingleClient, self).make_connection()

        self.__client_id = client_id

    def delete_single_client(self):

        with self._DBMakeConnection__conn:
            self._DBMakeConnection__cursor.execute("DELETE FROM tbl_client_list WHERE id = ?", (self.__client_id, ))

        #clear and close db
        self._DBMakeConnection__cursor.close()
        del self._DBMakeConnection__cursor

        self._DBMakeConnection__conn.close()
        del self._DBMakeConnection__conn

