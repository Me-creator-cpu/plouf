import sqlite3
import pandas as pd

data_path = './data/'
filename = 'database'
filenameFull = filename + '.sqlite3'
db = data_path + filenameFull

def db_get_path():
    global db
    return db

def db_connection():
    global db
    return sqlite3.connect(db)

def db_connection_close(conn, bCommit = False):
    if bCommit:
        conn.commit()
    conn.close()        

def db_commit(conn):
    conn.commit()

def db_exec_sql(sql,bScript=False):
    global db
    bExecSql=False
    #if bDebug:
    #    st.write(f'Exec SQL: {sql}')
    try:
        with db_connection() as conn:
            cur = conn.cursor()  
            if bScript:
                cur.executescript(sql)
            else:
                cur.execute(sql)
            conn.commit()
            bExecSql=True
    except sqlite3.OperationalError as e:
        #st.write(e)
        bExecSql=False
    db_connection_close(conn)
    return bExecSql

def db_drop_table(tablaname):
    db_exec_sql("DROP TABLE IF EXISTS " + tablaname)

def db_table_to_df(tablename,bShowTab=False):
    df = db_sql_to_df("SELECT * FROM " + tablename)
    if bShowTab:
        df
    return df

def db_sql_to_df(sql,bShowTab=False):
    df = pd.read_sql_query(sql, db_connection())
    if bShowTab:
        df
    return df


