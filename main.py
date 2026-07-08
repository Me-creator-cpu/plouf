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
        #open('idonotexist')
        open(db_fullpath)
        st.write('Database already exists!')
    except IOError as e:
        if e.args == 2: # No such file or directory
            #blank_db = sqlite3.connect('idontexist')
            blank_db = sqlite3.connect(db_fullpath)
            st.write(f'{db_fullpath} database created')
        else: # permission denied or something else?
            st.write(e)

def db_init_data_test(db_fullpath):
    connexion = sqlite3.connect(db_fullpath)
    curseur = connexion.cursor()
    donnees = [("toto", 1000), ("tata", 750), ("titi", 500)]
    curseur.execute("""CREATE TABLE IF NOT EXISTS scores(
                    id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                    pseudo TEXT,
                    valeur INTEGER
                    )""")
    curseur.executemany(
            "INSERT INTO scores (pseudo, valeur) VALUES (?, ?)",
            donnees)
    connexion.commit()
    connexion.close()
                    
def db_read_test(db_fullpath):
    connexion = sqlite3.connect(db_fullpath)
    #connexion = sqlite3.connect(":memory:") # BDD dans la RAM
    curseur = connexion.cursor() # Récupération d'un curseur
    curseur.execute("SELECT * FROM scores")
    for resultat in curseur:
            st.write(resultat)

    df = pd.read_sql_query("SELECT * FROM table_name", connexion)
    df
    connexion.close()

def init_buttons():
    global data_path,filename,filenameFull
    db = data_path + filenameFull
    if st.button('Create path'):
        st.write('Create...')
        os_build_path(db)

    if st.button('Create DB'):
        st.write('Create DB...')
        db_create2(db)

    if st.button('Create Data'):
        st.write('Create data...')
        db_init_data_test(db)

    if st.button('Get DB Data test'):
        st.write('Read DB...')
        db_read_test(db)

init_buttons()        