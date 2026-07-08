import streamlit as st
import pandas as pd
import datetime

import os
import sqlite3

data_path = './data/'
filename = 'database'
filenameFull = filename + '.sqlite3'

def os_build_path(pathtobuild):
    os.makedirs(pathtobuild, exist_ok=True)

def db_create(db_fullpath):
    db = sqlite3.connect(db_fullpath)
    db.execute('CREATE TABLE IF NOT EXISTS TableName (id INTEGER PRIMARY KEY, quantity INTEGER)')
    db.close()

def db_create2(db_fullpath):
    global data_path, filename,filenameFull
    try:
        open('idonotexist')
        st.write('Database already exists!')
    except IOError as e:
        if e.args == 2: # No such file or directory
            blank_db = sqlite3.connect('idontexist')
            st.write('Blank database created')
        else: # permission denied or something else?
            st.write(e)

def init_buttons():
    if st.button('Create path'):
        global data_path
        os_build_path(data_path)

    if st.button('Create DB'):
        global data_path,filenameFull
        db_create(data_path + filenameFull)

    if st.button('Get DB Data test'):
        st.empty()

init_buttons()        