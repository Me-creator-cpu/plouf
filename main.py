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

#def db_conn_check(conn):
#     try:
#        conn.cursor()
#        return True
#     except Exception as ex:
#        return False
#    #myconn = sqlite3.connect('test.db')
#    st.write(chk_conn(myconn))

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
    DROP TABLE IF EXISTS scores;

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

    df = pd.read_sql_query("SELECT * FROM scores", connexion)
    df

    connexion.close()

def db_drop_tests(db_fullpath):
    connexion = sqlite3.connect(db_fullpath)
    curseur = connexion.cursor()
    curseur.executescript("""DROP TABLE IF EXISTS TableName;
                          DROP TABLE IF EXISTS scores;""")
    connexion.commit()
    connexion.close()

#==================================================================================================
def db_connection(db_fullpath):
    return sqlite3.connect(db_fullpath)

def db_connection_close(conn, bCommit = False):
    if bCommit:
        conn.commit()
    conn.close()        

def db_commit(conn):
    conn.commit()

def db_table_to_df(tablename,conn,bShowTab=False):
    df = pd.read_sql_query("SELECT * FROM " + tablename, conn)
    if bShowTab:
        df
    return df

def db_init_data(db_fullpath):
    bAddParent = True
    bAddEnfant = False
    bAddResa = False

    connexion = sqlite3.connect(db_fullpath)
    curseur = connexion.cursor()

    if bAddParent:
                #  (parent_name, parent_tel, parent_mail)
        parents = [("arnaud", "0102030405","test1@mail.com"), 
                ("tata", "0607080910","test2@mail.com"), 
                ("titi", "0103050700","test3@mail.com")]
        curseur.execute("""CREATE TABLE IF NOT EXISTS t_parent(
                        parent_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        parent_name TEXT,
                        parent_tel TEXT,
                        parent_mail TEXT
                        )""")
        curseur.executemany(
                "INSERT INTO t_parent (parent_name, parent_tel, parent_mail) VALUES (?, ?, ?)",
                parents)
        connexion.commit()
        db_table_to_df("t_parent",connexion,True)
        
    if bAddEnfant:
                #  (enfant_name, parent_id, enfant_niveau, enfant_annee)
        enfants = [("eva", 0, 6, 2016), 
                ("jean", 0, 12, 2010), 
                ("paulo", 0, 12, 1994)]
        curseur.execute("""CREATE TABLE IF NOT EXISTS t_enfant(
                        enfant_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        enfant_name TEXT,
                        parent_id INTEGER,
                        enfant_niveau INTEGER,
                        enfant_annee INTEGER
                        )""")
        curseur.executemany(
                "INSERT INTO t_enfant (enfant_name, parent_id, enfant_niveau, enfant_annee) VALUES (?, ?, ?, ?)",
                enfants)
        connexion.commit()
        db_table_to_df("t_enfant",connexion,True)

    if bAddResa:
                       #(enfant_id, enfant_niveau, resa_date)
        reservations = [(),
                        (),
                        (),
                        (),
                        ()]
        curseur.execute("""CREATE TABLE IF NOT EXISTS t_reservation(
                        resa_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        enfant_id INTEGER,
                        enfant_niveau INTEGER,
                        resa_date TEXT
                        )""")
        curseur.executemany(
                "INSERT INTO t_reservation (enfant_id, enfant_niveau, resa_date) VALUES (?, ?, ?)",
                parents)
        connexion.commit()
        db_table_to_df("t_reservation",connexion,True)

    connexion.close()


#==================================================================================================

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

    if st.button("Init data"):
        db_drop_tests(db)
        db_init_data(db)

init_buttons()        