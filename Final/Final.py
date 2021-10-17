
#******************************************************************
# Author: Robert Webster
# Program: Client Management App
# Date: 10/03/2021
#  
# Comments: 
#
#
#******************************************************************

import os
import sys
import string
import sqlite3
import pyodbc
import pandas as pd
import database_create_sqlite3 as db_create_sqlite3

#choose database connection method
#import database_etl_sqlserver as db_conn
import database_etl_sqlite3 as db_conn

from PyQt5 import QtWidgets
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QApplication, QTableView
from application_windows import Ui_MainWindow

class MainApplication(QtWidgets.QMainWindow): 
    
    def __init__(self):              
        super(MainApplication, self).__init__()        
        self.ui = Ui_MainWindow()    
        self.ui.setupUi(self)

        #initialize variables
        self.__rec_id = ""
        self.__first_name = ""
        self.__last_name = ""
        self.__selected_service = ""

        #set design attributes
        self.style = "::section {""background-color: #E0E0E0; }" #set bg color of table header

        #set starting attributes
        self.ui.login_label_login_denied.setHidden(True)
        self.ui.label_welcome.setHidden(True)      
        self.ui.login_text_username.selectAll()
        self.ui.menu_list.setCurrentRow(0) 

        #initialize form
        self.__nav_login

        #establish signal and slots      
        self.__connectSignalsSlots() #define form actions and calls
    
    def __connectSignalsSlots(self):
        self.ui.login_btn_Sign_In.clicked.connect(self.__authenticate)
        self.ui.menu_btn_submit.clicked.connect(self.__form_main_menu_select)
        self.ui.client_list_btn_main.clicked.connect(self.__nav_main)
        self.ui.client_list_edit_btn_main.clicked.connect(self.__nav_main)
        self.ui.client_list_edit_btn_edit.clicked.connect(self.__nav_client_edit_profile)
        self.ui.client_edit_profile_btn_update.clicked.connect(self.__update_client)
        self.ui.client_edit_profile_btn_cancel.clicked.connect(self.__nav_client_list_edit)
        self.ui.add_client_btn_add.clicked.connect(self.__add_client)
        self.ui.add_client_btn_cancel.clicked.connect(self.__nav_main)
        self.ui.client_list_delete_btn_delete.clicked.connect(self.__delete_client)
        self.ui.client_list_delete_btn_main.clicked.connect(self.__nav_main)

    def __authenticate(self):        
        #get values of username and password
        self.__form_login_username = self.ui.login_text_username.text()
        self.__form_login_password = self.ui.login_text_password.text()

        #input validation
        self.__obj_inputvalidation = InputValidation(self.__form_login_username)
        self.__check_punctuation = self.__obj_inputvalidation.check_has_punctuation()

        if self.__check_punctuation == "True":            
            self.ui.login_label_login_denied.setHidden(False) #make label visible       
            self.ui.login_label_login_denied.setText("Punctuation not allowed in Username") #change text 

        else:
            ##get pw from sql
            self.__obj_db = db_conn.DBAuthenticate(self.__form_login_username)
            self.__results = self.__obj_db.authenticate()

            if self.__results == None:
                #access denied
                self.ui.login_label_login_denied.setHidden(False) #make label visible       
                self.ui.login_label_login_denied.setText("Please enter Username and Password") #change text          

            else:
                self.__first_name= self.__results[1]
                self.__last_name = self.__results[2]
                self.__pw = self.__results[4]

                if  self.__pw == self.__form_login_password:
                    #access granted
                    self.ui.login_label_login_denied.setHidden(True) #hide label
                    self.ui.label_welcome.setHidden(False) #unhide label
                    self.ui.label_welcome.setText("Welcome " + self.__first_name + " " + self.__last_name) #change text

                    #form navigation
                    self.__nav_main()        
                
                else:
                    #access denied
                    self.ui.login_label_login_denied.setHidden(False) #make label visible       
                    self.ui.login_label_login_denied.setText("Incorrect Username/Password") #change text
      
    def __form_main_menu_select(self):

        #get value from list widget
        self.__form_list_select = self.ui.menu_list.currentItem().text()

        #check to see if an item is selected
        self.__items = self.ui.menu_list.selectedItems()
        self.__selected_item = []

        for i in list(self.__items):
                self.__selected_item.append(str(i.text()))

        if self.__selected_item: #boolean if not empty

            #execute based on menu selection
            if self.__form_list_select == "DISPLAY client list":
                #form navigation
                self.__nav_client_list()                                     

            elif self.__form_list_select == "EDIT a client":
                #form navigation
                self.__nav_client_list_edit()

            elif self.__form_list_select == "ADD a new client":
                #form navigation
                self.__nav_add_client()                

            elif self.__form_list_select == "DELETE a client":
                #form navigation
                self.__nav_client_delete()  

            elif self.form_list_select == "Exit the program":
                sys.exit()
        else:
            pass
 
    def __get_client_list(self, widget_name, get_type, id):

        self.__widget_name = widget_name
        self.__get_type = get_type
        self.__id = id

        if self.__get_type == "all":

            #get client list
            obj_1 = db_conn.DBGetAllClients()
            self.clients = obj_1.get_all_clients()
            df = pd.DataFrame(self.clients)
            model = pandasModel(df)

            set_model = "self.ui." + widget_name + ".setModel(model)"
            exec(set_model)

        elif get_type == "one": 

            #get client list
            obj_2 = db_conn.DBGetSingleClient(self.__id)
            self.client = obj_2.get_single_client()
            df = pd.DataFrame(self.client)
            model = pandasModel(df)

            set_model = "self.ui." + widget_name + ".setModel(model)"
            exec(set_model)

            #get values from data frame
            self.__rec_id = str(df.iloc[0][0])
            self.__first_name = str(df.iloc[0][1])
            self.__last_name = str(df.iloc[0][2])
            self.__selected_service = str(df.iloc[0][3])

        #disable widget select ability
        self.__disable_select_1 = "self.ui." + self.__widget_name + ".setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)"
        self.__disable_select_2 = "self.ui." + self.__widget_name + ".setFocusPolicy(Qt.NoFocus)"
        self.__disable_select_3 = "self.ui." + self.__widget_name + ".setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)"
        exec(self.__disable_select_1), exec(self.__disable_select_2), exec(self.__disable_select_3)

        #set column widths
        self.__col_width_1 = "self.ui." + self.__widget_name + ".horizontalHeader()"
        self.__col_width_2 = "self.ui." + self.__widget_name + ".horizontalHeader().resizeSection(0, 25)"
        self.__col_width_3 = "self.ui." + self.__widget_name + ".horizontalHeader().resizeSection(1, 220)"
        self.__col_width_4 = "self.ui." + self.__widget_name + ".horizontalHeader().resizeSection(2, 220)"
        self.__col_width_5 = "self.ui." + self.__widget_name + ".horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)"
        self.__col_width_6 = "self.ui." + self.__widget_name + ".horizontalHeader().setDefaultAlignment(Qt.AlignLeft)"
        exec(self.__col_width_1), exec(self.__col_width_2), exec(self.__col_width_3)
        exec(self.__col_width_4), exec(self.__col_width_5), exec(self.__col_width_6)

        #reset vertical scroll to top
        self.__reset_scroll = "self.ui." + self.__widget_name + ".scrollTo(self.ui." + widget_name + ".model().index(0, 0))"        
        exec(self.__reset_scroll)

        #set header bg color
        self.__header_color = "self.ui." + self.__widget_name + ".horizontalHeader().setStyleSheet(self.style)"
        exec(self.__header_color)  

    def __update_client(self):

        #get text from label
        self.__id = self.ui.client_list_edit_enter_id.text()
        self.__first_name = self.ui.client_edit_profile_first_name.text()
        self.__last_name = self.ui.client_edit_profile_last_name.text()
        self.__selected_service = self.ui.client_edit_profile_cmb_service.currentText()

        #pass data to sql table
        ManageClient.edit_client_list(self, self.__id, self.__first_name, self.__last_name, self.__selected_service)

        #form navigation
        self.__nav_client_edit_profile() 

    def __add_client(self):

        #get form input
        self.__form_first_name = self.ui.add_client_text_first_name.text()
        self.__form_last_name = self.ui.add_client_text_last_name.text()
        self.__form_selected_service = self.ui.add_client_cmb_service.currentText()       

        if self.__form_first_name != "First Name" and  self.__form_last_name != 'Last Name':           

            #pass data to sql table
            ManageClient.add_client(self, self.__form_first_name, self.__form_last_name, self.__form_selected_service)

            #form navigation
            self.__nav_client_list()               

    def __delete_client(self):

        #get text from label
        self.__id = self.ui.client_list_delete_enter_id.text()

        #input validation
        self.__obj_inputvalidation = InputValidation(self.__id)
        self.__check_digit = self.__obj_inputvalidation.check_has_digits()

        if self.__check_digit == "True":

            #pass data to sql table
            ManageClient.delete_client(self, self.__id)

            #form navigation
            self.__nav_client_delete()
        else:
            self.ui.client_list_delete_enter_id.setText("Enter ID")
            self.ui.client_list_delete_enter_id.setFocus()
            self.ui.client_list_delete_enter_id.selectAll()              

    def __nav_login(self):

        #iniialize form
        self.ui.stackedWidget.setCurrentWidget(self.ui.login)

    def __nav_main(self):

        #iniialize form
        self.ui.stackedWidget.setCurrentWidget(self.ui.main)  
        
        self.ui.menu_list.setCurrentRow(0) #set to default

    def __nav_client_list(self):

        self.__id = 0

        #iniialize form
        self.ui.stackedWidget.setCurrentWidget(self.ui.client_list)

        #reset form fields
        self.ui.add_client_text_first_name.setText('First Name')
        self.ui.add_client_text_last_name.setText('Last Name')
        self.ui.add_client_cmb_service.setCurrentIndex(0)
        self.ui.add_client_text_first_name.selectAll()

        #get client list for table widget
        self.__widget_name = "client_list_list"
        self.__get_type = "all" #all or one client(s)
        self.__get_client_list(self.__widget_name, self.__get_type, self.__id)
   
    def __nav_client_list_edit(self):

        self.__id = ""

        #iniialize form
        self.ui.stackedWidget.setCurrentWidget(self.ui.client_list_edit)

        self.ui.client_list_edit_enter_id.setText("Enter ID")
        self.ui.client_list_edit_enter_id.selectAll()
        self.ui.client_list_edit_enter_id.setFocus()

        self.ui.client_edit_profile_first_name.setText("First Name")
        self.ui.client_edit_profile_last_name.setText("Last Name")
        self.ui.client_edit_profile_cmb_service.setCurrentIndex(0)   
        
        #get client list for table widget
        self.__widget_name = "client_list_edit_list"
        self.__get_type = "all" #all or one client(s)
        self.__get_client_list(self.__widget_name, self.__get_type, self.__id)

    def __nav_client_edit_profile(self):

        #get client id
        self.__id = self.ui.client_list_edit_enter_id.text()

        #input validation
        self.__obj_inputvalidation = InputValidation(self.__id)
        self.__check_digit = self.__obj_inputvalidation.check_has_digits()

        if self.__check_digit == "True":

            #iniialize form
            self.ui.stackedWidget.setCurrentWidget(self.ui.client_edit_profile)

            #get client list for table widget
            self.__widget_name = "client_edit_profile_list"
            self.__get_type = "one" #all or one client(s)
            self.__get_client_list(self.__widget_name, self.__get_type, self.__id)

            #set text
            self.ui.client_edit_profile_first_name.setText(self.__first_name)
            self.ui.client_edit_profile_last_name.setText(self.__last_name)

            if self.__selected_service == "Brokerage":
                self.ui.client_edit_profile_cmb_service.setCurrentIndex(0)
            elif self.__selected_service == "Retirement":
                self.ui.client_edit_profile_cmb_service.setCurrentIndex(1)

        else:
            self.ui.client_list_edit_enter_id.setText("Enter ID")
            self.ui.client_list_edit_enter_id.selectAll()
            self.ui.client_list_edit_enter_id.setFocus()

    def __nav_add_client(self):

        #iniialize form
        self.ui.stackedWidget.setCurrentWidget(self.ui.add_client)

        #select all of form box
        self.ui.add_client_text_first_name.selectAll()
        self.ui.add_client_text_first_name.setFocus()

    def __nav_client_delete(self):

        self.__id = ""

        #iniialize form
        self.ui.stackedWidget.setCurrentWidget(self.ui.client_delete)

        self.ui.client_list_delete_enter_id.setText("Enter ID")
        self.ui.client_list_delete_enter_id.setFocus()
        self.ui.client_list_delete_enter_id.selectAll()

     #get client list for table widget
        self.__widget_name = "client_list_delete_list"
        self.__get_type = "all" #all or one client(s)
        self.__get_client_list(self.__widget_name, self.__get_type, self.__id)

    def __nav_delete_client_profile(self):

        #iniialize form
        self.ui.stackedWidget.setCurrentWidget(self.ui.__delete_client_profile)


class ManageClient(object):

    def edit_client_list(self, id, first_name, last_name, selected_service):

        self.__id = id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__selected_service = selected_service

        #update client in database
        self.__obj_1 = db_conn.DBUpdateSingleClient(self.__id, self.__first_name, self.__last_name, self.__selected_service)
        self.__obj_1.update_single_client()

    def add_client(self, first_name, last_name, selected_service):

        self.__first_name = first_name
        self.__last_name = last_name
        self.__selected_service = selected_service

        #add client in database      
        self.__obj_1 = db_conn.DBAddSingleClient(self.__first_name, self.__last_name, self.__selected_service)
        self.__obj_1.add_single_client()

    def delete_client(self, id):

        self.__id = id

        #delete client in database
        self.__obj_1 = db_conn.DBDeleteSingleClient(self.__id)
        self.__obj_1.delete_single_client()

class pandasModel(QAbstractTableModel):

    def __init__(self, data):

        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):

        return self._data.shape[0]

    def columnCount(self, parnet=None):

        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):

        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])

        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]

        return None

class InputValidation(object):     

    def __init__(self, input_string):

        self.__input_string = input_string
          
    def check_has_punctuation(self):

        if any(char in string.punctuation for char in self.__input_string):
            return "True"
        else:
            return "False"

    def check_has_digits(self):

        if any(char in string.digits for char in self.__input_string):
            return "True"
        else:
            return "False"

    def check_has_ascii(self):

        if any(char in string.ascii_letter for char in self.__input_string):
            return "True"
        else:
            return "False"



def main():

    if __name__ == "__main__":

        #create new database if does not exists
        database_path = os.environ['TEMP'] + '\cma.db'
        database_exists = os.path.exists(database_path)

        if database_exists == False:

            obj_db = db_create_sqlite3.CreateDB()
            obj_db.create_table_data()

        #start application
        app = QtWidgets.QApplication([])
        application = MainApplication()
        application.show()

    try:
        sys.exit(app.exec())
    except:
        print("Exiting")


main()


