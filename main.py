import streamlit as st
import pandas as pd
import datetime
import locale

import os
import sqlite3

data_path = './data/'
filename = 'database'
filenameFull = filename + '.sqlite3'
db = data_path + filenameFull

locale.setlocale(locale.LC_ALL, "fr_FR")

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

def db_exec_sql(sql):
    global db
    st.write(f'Exec SQL: {sql}')
    try:
        with db_connection(db) as conn:
            cur = conn.cursor()  
            cur.execute(sql)
            conn.commit()
    except sqlite3.OperationalError as e:
        st.write(e)
    db_connection_close(conn)

def db_table_to_df(tablename,conn,bShowTab=False):
    df = pd.read_sql_query("SELECT * FROM " + tablename, conn)
    if bShowTab:
        df
    return df

def db_init_data(db_fullpath):
    bAddParent = False
    bAddEnfant = False
    bAddResa = False
    bShowTable = not(bAddParent) and not(bAddEnfant) and not(bAddResa)

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
        enfants = [("eva", 1, 6, 2016), 
                ("jean", 1, 12, 2010), 
                ("paulo", 3, 12, 1994)]
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
        reservations = [(1,6,"11/07/2026"),
                        (2,12,"18/07/2026"),
                        (3,12,"17/07/2026"),
                        (1,6,"11/07/2026"),
                        (3,12,"13/07/2026")]
        curseur.execute("""CREATE TABLE IF NOT EXISTS t_reservation(
                        resa_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        enfant_id INTEGER,
                        enfant_niveau INTEGER,
                        resa_date TEXT
                        )""")
        curseur.executemany(
                "INSERT INTO t_reservation (enfant_id, enfant_niveau, resa_date) VALUES (?, ?, ?)",
                reservations)
        connexion.commit()
        db_table_to_df("t_reservation",connexion,True)

    if bShowTable:
        db_table_to_df("t_parent",connexion,True)
        db_table_to_df("t_enfant",connexion,True)
        db_table_to_df("t_reservation",connexion,True)

    connexion.close()


#==================================================================================================

def init_buttons():
    global data_path,filename,filenameFull, db
    #db = data_path + filenameFull
    if 1 == 2:
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

#==================================================================================================
# Fonctions données
#==================================================================================================
def highlight_changes(val):
    color = f"color: black;" if val else "color:lightgray;"
    background = f"background-color:lightgray;" if val else ""
    return f"{color} {background}"

def show_diff(
    source_df: pd.DataFrame, modified_df: pd.DataFrame, editor_key: dict, table_name: str, key_field: str
) -> None:
    target = pd.DataFrame(editor_key.get("edited_rows")).transpose().reset_index()
    modified_columns = [i for i in target.notna().columns if i != "index"]
    source = source_df.iloc[target['index']].reset_index()
    bRefresh = False
    
    st.divider()
    st.write('Source:')
    source #.iloc[source[key_field]]
    st.write('Target:')
    target
    target_base = target.copy()
    st.divider()
    
    target = target[modified_columns].reset_index()

    changes = pd.merge(
        source[modified_columns].reset_index(),
        target,
        how="outer",
        on="index",
        suffixes=["_BEFORE", "_AFTER"],
    )
    after_columns = [i for i in changes.columns if "_AFTER" in i]
    for cl in changes:
        if cl in after_columns:
            new_col = cl.replace("_AFTER", "_BEFORE")
            changes[cl] = changes[cl].fillna(changes[new_col])

    st.subheader("Données modifiées")
    st.caption("Colonnes modifiées uniquement")

    change_markers = changes.copy()
    for cl in change_markers:
        if cl in after_columns:
            new_col = cl.replace("_AFTER", "_BEFORE")
            change_markers[cl] = change_markers[cl] != change_markers[new_col]
            change_markers[new_col] = change_markers[cl]
    if 1 == 2:    
        st.dataframe(
            changes.style.apply(
                lambda _: change_markers.applymap(highlight_changes), axis=None
            ),
            width='stretch',
            hide_index=True,
        )
    st.dataframe( 
        changes,
        width='stretch',
        hide_index=True,
    )
    if st.button('Test update'):
        target_base=target_base.fillna('#####')
        rows, cols = target_base.shape
        #st.write(rows, cols)
        sql=''
        id=0
        for r in range(rows):
            st.write(f'r = {r}')
            st.write(f'{key_field} = {target_base['index'][r]}')
            src_col=key_field
            src_row=source.iloc[r][key_field]
            st.write(f'src_row={src_row}')
            st.write(f'source {key_field} = {source[{key_field}][src_row]}')
            id=int(source.iloc[r][key_field])
            for c in target_base:
                if c != 'index':
                    if target_base[c][r] != '#####':
                        #st.write(f'updated field={c}')
                        #st.write(f'New {c} = {target_base[c][r]}')
                        sql = f"UPDATE {table_name} SET {c}='{target_base[c][r]}' WHERE {key_field} = {id}"
                        st.write(sql)
                        #db_exec_sql(sql)
                        #bRefresh=True

    st.subheader("Lignes créées")
    inserted = pd.DataFrame(editor_key.get("added_rows"))
    st.dataframe(inserted, width='stretch')
    st.subheader("Lignes supprimées")
    deleted = pd.DataFrame(editor_key.get("deleted_rows"))
    st.dataframe(deleted, width='stretch')
    if st.button('Delete data'):
        rows, cols = deleted.shape
        for r in range(rows):
            st.write(f'{key_field} = {deleted['index'][r]}')

    if bRefresh:
        st.session_state["parent_edit"] = None

def get_cell_value(d,src,ret,valsrc):
    #data_type.get("Color")[data_type["Type"].index("Fire")]
    try:
        return d.get(ret)[d[src].index(valsrc)]
    except:
        return None


def db_parents_get(ID_Parent = None):
    global db
    connexion=db_connection(db)  
    if ID_Parent is not None:
        st.write(f'Filtering for {ID_Parent}')
        df = pd.read_sql_query("SELECT * FROM t_parent WHERE parent_id = " + str(ID_Parent), connexion)
        db_connection_close(connexion)
        return pd.DataFrame(df)
        df2 = pd.DataFrame(df)
        df2
        #filtered_df = df[df['Department'] == 'Marketing']
        filtered_df = df2[df2['parent_id'] == int(ID_Parent)] #.copy(deep=True)
        filtered_df
        return filtered_df
        #return df
    else:
        df = db_table_to_df("t_parent",connexion,True)
        db_connection_close(connexion)
        return df

def db_parents_update(id,name,tel,email):
    global db
    sql = f'UPDATE t_parent SET parent_name){name} parent_email={email}, parent_tel={tel}  WHERE parent_id={id}'
    try:
        with db_connection(db) as conn:
            cur = conn.cursor()  
            cur.execute(sql)
            conn.commit()
    except sqlite3.OperationalError as e:
        st.write(e)
    db_connection_close(conn)

def pg_parent_adm():
    global db
    connexion=db_connection(db)  
    df = db_table_to_df("t_parent",connexion,False)
    db_connection_close(connexion)
    st.subheader("Liste des parents ⬇️")
    editor_df = st.data_editor(
        df, 
        key="parent_edit", 
        num_rows="dynamic", 
        use_container_width=True,
        disabled=["parent_id"],
        hide_index=True,
    )

    show_diff(source_df=df, modified_df=editor_df, editor_key=st.session_state["parent_edit"],table_name='t_parent', key_field='parent_id')
    return True
    df_updated=st.session_state["parent_edit"]
    st.write(df_updated) 

    st.divider()
    df_edited  = df_updated.get("edited_rows")
    st.write(df_edited)
    if st.button('Mettre à jour'):
        target = pd.DataFrame(df_edited).transpose().reset_index()
        modified_columns = [i for i in pd.DataFrame(df_edited).notna().columns if i != "index"]
        st.write('modified_columns')
        modified_columns
        st.write('loop upd')
        for u in df_edited:
            st.write(df.loc[u]['parent_id'])
            #db_parents_update(df.loc[u]['parent_id'],df.loc[u]['parent_name'],df.loc[u]['parent_id'],df.loc[u]['parent_email'])
    st.divider()
    df_added   = df_updated.get("added_rows")
    st.write(df_added)
    st.divider()
    df_deleted = df_updated.get("deleted_rows")
    st.write(df_deleted)


#==================================================================================================
# Pages
#==================================================================================================
# Parents =========================================================================================
def pg_parent_get():
    db_parents_get()
    db_parents_get(2)

def pg_parent_create():
    st.empty()

def pg_parent_update():
    st.empty()

def pg_parent_delete():
    st.empty()
# Enfant ==========================================================================================
def pg_enfant_get():
    global db
    connexion=db_connection(db)
    db_table_to_df("t_enfant",connexion,True)
    db_connection_close(connexion)

def pg_enfant_create():
    st.empty()

def pg_enfant_update():
    st.empty()

def pg_enfant_delete():
    st.empty()
# Resa ============================================================================================
def pg_resa_get():
    global db
    connexion=db_connection(db)
    db_table_to_df("t_reservation",connexion,True)
    db_connection_close(connexion)


def pg_resa_create():
    st.empty()

def pg_resa_update():
    st.empty()

def pg_resa_delete():
    st.empty()
#==================================================================================================
def pg_home():
    st.empty()

def pg_empty(x=1):
    st.empty()

def pg_init_data():
    init_buttons()

app_title = 'Plouf Plouf'

st.set_page_config(
    page_title=app_title,
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
#    menu_items={        # <===================================== #top right menu (triple dots) near GitHub icon
#        'Get Help': 'https://www.extremelycoolapp.com/help',
#        'Report a bug': "https://www.extremelycoolapp.com/bug",
#        'About': "# This is a header. This is an *extremely* cool app!"
#    }
)

with st.sidebar:
    top_nav = st.toggle('Menu top', False)
    nav_sections = st.toggle('Avec rubriques', True)

pages = {
    'Home':[ 
        st.Page(pg_home, title='Home', icon="🏠"),
    ],
    'Init data':[
        st.Page(pg_init_data, title='Init data', icon="🚀"),
    ],
    'User':[
        st.Page(pg_enfant_get, title='Enfant', icon="🚀"),
        st.Page(pg_resa_create, title='Réservation', icon="🧰"),
        st.Page(pg_resa_update, title='Planning enfant', icon="📅"),
    ],
    'Admin': [
        st.Page(pg_parent_adm, title='Gérer parents',icon="🌟"),
        st.Page(pg_enfant_create, title='Gérer enfants',icon="🧬"),
        st.Page(pg_resa_get, title='Voir réservations',icon="🧬"),
        st.Page(pg_empty, title='Planning prof',icon="📅"),
    ],
}

pg = st.navigation(
    pages if nav_sections else [page for section in pages.values() for page in section],
    position="top" if top_nav else "sidebar"
)
pg.run()
        