import streamlit as st
import pandas as pd
#import datetime
from datetime import timedelta
from datetime import datetime
from datetime import time
import locale

import os
import sqlite3
import re

from streamlit_calendar import calendar

#Login
import hashlib

from pictures import *
from db_funcs import *

#GitHub 
from pathlib import Path
from github import Auth
from github import Github

#https://gist.github.com/GeorgePearse/bb951fde95fded5b2a1323fc1c29b8e7

#data_path = './data/'
#filename = 'database'
#filenameFull = filename + '.sqlite3'
#db = data_path + filenameFull

bDebug=False
#bDebug=True

locale.setlocale(locale.LC_ALL, "fr_FR")

col_pct=st.column_config.NumberColumn(
        min_value=0,
        max_value=100,
        format="percent",
    )

col_parent_select=st.column_config.SelectboxColumn(
            "Parent",
            width="medium",
            options=[
                "📊 Data Exploration",
                "📈 Data Visualization",
                "🤖 LLM",
            ],
            required=True,
        )

column_config_parent={
    "parent_id": st.column_config.NumberColumn( "ID", pinned = True ),
    "parent_name": st.column_config.TextColumn( "Nom"),
    "parent_tel": st.column_config.TextColumn( "Tél."),
    "parent_mail":st.column_config.TextColumn( "EMail"),
    "parent_id_del": st.column_config.CheckboxColumn("Désactivé"),
    "parent_id_del_s": st.column_config.NumberColumn(
        "Actif",
        min_value=0,
        max_value=1,
        format="%d ⭐",
    )
}

column_config_enfant={
    "parent_id": None, #st.column_config.NumberColumn( "Parent",),
    "parent_name":st.column_config.TextColumn("Nom parent"),
    "enfant_id": st.column_config.NumberColumn( "ID", pinned = True ),
    "enfant_name": st.column_config.TextColumn( "Prénom"),
    "enfant_annee":st.column_config.NumberColumn( "Né en"),
    "enfant_niveau": st.column_config.NumberColumn(
        "Niveau",
        min_value=0,
        max_value=12,
        format="%d ⭐",
    ),
    "enfant_age": st.column_config.NumberColumn("Age"),
    "parent_new": st.column_config.SelectboxColumn(
            "Parent (nouveau)",
            width="medium",
            options=[
                "📊 Data Exploration",
                "📈 Data Visualization",
                "🤖 LLM",
            ],
            required=True,
        )
}

def os_build_path(pathtobuild):
    os.makedirs(pathtobuild, exist_ok=True)

#==================================================================================================

def db_init_data(bAddParent=False,bAddEnfant=False,bAddResa=False):
    bShowTable = not(bAddParent) and not(bAddEnfant) and not(bAddResa)

    connexion = db_connection()
    curseur = connexion.cursor()

    if bAddParent:
        parents = [("arnaud", "0102030405","test1@mail.com",0), 
                ("tata", "0607080910","test2@mail.com",0), 
                ("titi", "0103050700","test3@mail.com",0)]
        curseur.executescript("DROP TABLE IF EXISTS t_parent;")
        connexion.commit()
        curseur.execute("""CREATE TABLE IF NOT EXISTS t_parent(
                        parent_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        parent_name TEXT,
                        parent_tel TEXT,
                        parent_mail TEXT,
                        parent_id_del INTEGER
                        )""")
        curseur.executemany(
                "INSERT INTO t_parent (parent_name, parent_tel, parent_mail,parent_id_del) VALUES (?, ?, ?, ?)",
                parents)
        connexion.commit()
        db_table_to_df("t_parent",True)
        
    if bAddEnfant:
        enfants = [("eva", 1, 6, 2016), 
                ("jean", 1, 12, 2010), 
                ("paulo", 3, 12, 1994)]
        curseur.executescript("DROP TABLE IF EXISTS t_enfant;")
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
        db_table_to_df("t_enfant",True)

    if bAddResa:
        reservations = [(1,"11/07/2026","14:00"),
                        (2,"18/07/2026","15:35"),
                        (3,"17/07/2026","14:35"),
                        (1,"11/07/2026","14:35"),
                        (3,"13/07/2026","16:00")]
        curseur.executescript("DROP TABLE IF EXISTS t_reservation;")
        curseur.execute("""CREATE TABLE IF NOT EXISTS t_reservation(
                        resa_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
                        enfant_id INTEGER,
                        resa_date TEXT,
                        resa_heure TEXT
                        )""")
        curseur.executemany(
                "INSERT INTO t_reservation (enfant_id, resa_date, resa_heure) VALUES (?, ?, ?)",
                reservations)
        connexion.commit()
        db_table_to_df("t_reservation",True)

    if bShowTable:
        db_table_to_df("t_parent",True)
        db_table_to_df("t_enfant",True)
        db_table_to_df("t_reservation",True)

    db_connection_close(connexion)

#==================================================================================================

def init_buttons():
    subtitle('Initialisation données tests')
    bAddParent = st.toggle('Parents',True)
    bAddEnfant = st.toggle('Enfants',False)
    bAddResa = st.toggle('Réservtions',False)
    if st.button("Init data"):
        db_init_data(bAddParent,bAddEnfant,bAddResa)

#==================================================================================================
# Fonctions données
#==================================================================================================
def highlight_changes(val):
    color = f"color: black;" if val else "color:lightgray;"
    background = f"background-color:lightgray;" if val else ""
    return f"{color} {background}"

def has_data(df):
    try:
        rows, cols = df.shape
        if rows > 0:
            return True
        else:
            return False
    except:
        return False
    
def age(year_born=2026):
    #return datetime.datetime.now().year-year_born
    return datetime.now().year-year_born

def show_diff(
    source_df: pd.DataFrame, modified_df: pd.DataFrame, editor_key: dict, table_name: str, key_field: str
) -> None:
    global db,bDebug
    target = pd.DataFrame(editor_key.get("edited_rows")).transpose().reset_index()
    target_base = target.copy()
    modified_columns = [i for i in target.notna().columns if i != "index"]
    source = source_df.iloc[target['index']].reset_index()
    bRefresh = False
    
    if bDebug:
        with st.expander('Inputs',expanded=False):
            st.divider()
            st.write('Source:')
            source #.iloc[source[key_field]]
            st.write('Target:')
            target
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
    
    bStatus=False
    col1, col2, col3 = st.columns(3)

    with col1:
        subtitle("Données modifiées")

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
        st.caption("Colonnes modifiées uniquement")
        if st.button('Mettre à jour',disabled=not has_data(target_base)): 
            bStatus=False
            target_base=target_base.fillna('#####')
            rows, cols = target_base.shape
            #st.write(rows, cols)
            sql=''
            id=0

            conn = db_connection()
            for r in range(rows):
                id=int(source.iloc[r][key_field])
                for c in target_base:
                    if c != 'index':
                        if target_base[c][r] != '#####':
                            sql = f"UPDATE {table_name} SET {c}='{target_base[c][r]}' WHERE {key_field} = {id}"
                            if c.lower().endswith("_mail"):
                                if email_valid(target_base[c][r]):
                                    cur = conn.cursor()
                                    cur.execute(sql)
                            else:
                                cur = conn.cursor()
                                cur.execute(sql)

                            if bDebug:
                                st.write(sql)
                            #bStatus = bStatus or db_exec_sql(sql)
                            bRefresh=True
            
            try:
                conn.commit()
                bStatus=True
            except sqlite3.OperationalError as e:
                st.write(e)
                bStatus=False
            db_connection_close(conn)

            if bStatus:
                st.success('Mise à jour effectuée')
            else:
                st.warning('Erreur dans la mise à jour')

    with col2:
        subtitle("Lignes créées")
        inserted = pd.DataFrame(editor_key.get("added_rows"))
        st.dataframe(inserted, width='stretch')
        
        if st.button('Ajouter', disabled=not has_data(inserted)):
            rows, cols = inserted.shape
            sql=''

            bStatus=False
            conn = db_connection()
            for r in range(rows):
                id=0
                fld_lst=''
                fld_val=''
                bKeyValid=True
                for c in inserted.columns:
                    col=c
                    val=inserted[c][r]
                    if col == key_field:
                        bKeyValid=True
                    st.write(f'colname={col},value={val}')
                    if fld_lst=='':
                        fld_lst += col
                        fld_val += "'"+val+"'"
                    else:
                        fld_lst += ", "+col
                        fld_val += ", '"+val+"'"
                if bKeyValid:
                    #INSERT INTO {table_name} (parent_name, parent_tel, parent_mail) VALUES (?, ?, ?)
                    sql = f"INSERT INTO {table_name} ({fld_lst}) VALUES ({fld_val})"
                    if bDebug:
                        st.write(sql)
                    cur = conn.cursor()
                    cur.execute(sql)
            try:
                conn.commit()
                bStatus=True
            except sqlite3.OperationalError as e:
                st.write(e)
                bStatus=False
            db_connection_close(conn)

            if bStatus:
                st.success('Création effectuée')
            else:
                st.warning('Erreur dans la création')

    with col3:
        subtitle("Lignes supprimées")
        deleted = pd.DataFrame(editor_key.get("deleted_rows"))
        st.dataframe(deleted, width='stretch')
        if st.button('Supprimer', disabled=not has_data(deleted)):
            rows, cols = deleted.shape
            sql=''
            id=0
            bStatus=False
            conn = db_connection()
            for r in range(rows):
                id=int(deleted[0][r])
                #sql = f"DELETE FROM {table_name} WHERE {key_field} = {id}"
                if table_name == 't_parent':
                    sql = f"UPDATE {table_name} SET {key_field}_del=1 WHERE {key_field} = {id}"
                else:
                    sql = f"DELETE FROM {table_name} WHERE {key_field} = {id}"
                if bDebug:
                    st.write(sql)
                cur = conn.cursor()
                cur.execute(sql)
            
            try:
                conn.commit()
                bStatus=True
            except sqlite3.OperationalError as e:
                st.write(e)
                bStatus=False
            db_connection_close(conn)

            if bStatus:
                st.success('Suppression effectuée')
            else:
                st.warning('Erreur dans la suppression')


#    if bRefresh:
#        st.session_state["parent_edit"] = None

def get_cell_value(d,src,ret,valsrc):
    #data_type.get("Color")[data_type["Type"].index("Fire")]
    try:
        return d.get(ret)[d[src].index(valsrc)]
    except:
        return None

def subtitle(txt=''):
    st.subheader(f'{txt}',divider=True)

def email_valid(email):
    email_validate_pattern = r"^\S+@\S+\.\S+$"
    ret=False
    try:
        chk=re.match(email_validate_pattern, email)
        ret=False if chk is None else True
    except:
        ret=False
    return ret

def db_parents_get(ID_Parent = None): 
    if ID_Parent is not None:
        st.write(f'Filtering for {ID_Parent}')
        df = db_sql_to_df("SELECT * FROM t_parent WHERE parent_id = " + str(ID_Parent))
        return pd.DataFrame(df)
    else:
        df = db_table_to_df("t_parent",True)
        return df

def db_parents_update(id,name,tel,email):
    global db
    sql = f'UPDATE t_parent SET parent_name){name} parent_email={email}, parent_tel={tel}  WHERE parent_id={id}'
    try:
        with db_connection() as conn:
            cur = conn.cursor()  
            cur.execute(sql)
            conn.commit()
    except sqlite3.OperationalError as e:
        st.write(e)
    db_connection_close(conn)

def pg_parent_adm():
    df = db_table_to_df("t_parent",False)
    subtitle("Liste des parents ⬇️")
    editor_df = st.data_editor(
        df, 
        column_config=column_config_parent,
        key="parent_edit", 
        num_rows="dynamic", 
        width='stretch',
        disabled=["parent_id"],
        hide_index=True,
    )

    show_diff(source_df=df, modified_df=editor_df, editor_key=st.session_state["parent_edit"],table_name='t_parent', key_field='parent_id')
    return True

def pg_enfant_adm():
    df = db_table_to_df("t_enfant",False)
    df_parent = db_sql_to_df("SELECT parent_id,parent_name FROM t_parent")
    #lst_parents = connexion.cursor().execute('SELECT parent_id,parent_name FROM t_parent').fetchall()

    subtitle("Liste des enfants ⬇️")

    df = pd.merge(df, df_parent, how="left", on=["parent_id", "parent_id"])

    values = df_parent['parent_name'].tolist()
    options = df_parent['parent_id'].tolist()
    dic = dict(zip(options, values))
    sel_parent = st.selectbox('Parent', options, format_func=lambda x: dic[x])
    #st.write(a)
    df_filtered = df[df['parent_id'] == int(sel_parent)]
    #df_filtered['enfant_age']=datetime.datetime.now().year-df_filtered['enfant_annee']
    df_filtered['enfant_age']=age(df_filtered['enfant_annee'])

    column_config_enfant2={
        #"parent_id": None, #st.column_config.NumberColumn( "Parent",),
        #"parent_name":st.column_config.TextColumn("Nom parent"),
        "enfant_id": st.column_config.NumberColumn( "ID", pinned = True ),
        "enfant_name": st.column_config.TextColumn( "Prénom"),
        "enfant_annee":st.column_config.NumberColumn( "Né en"),
        "enfant_niveau": st.column_config.NumberColumn(
            "Niveau",
            min_value=0,
            max_value=12,
            format="%d ⭐",
        ),
        "enfant_age": st.column_config.NumberColumn("Age"),
        "parent_id": st.column_config.SelectboxColumn(
                "Nom parent",
                width="medium",
                options=options,
                format_func=lambda x: dic[x],
                required=True,
            )
    }

    editor_df = st.data_editor(
        df_filtered, 
        column_config=column_config_enfant2,
        column_order=['enfant_id','enfant_name','enfant_niveau','enfant_age','enfant_annee','parent_id'],
        key="enfant_edit", 
        num_rows="dynamic", 
        width='stretch',
        disabled=["enfant_id"],
        hide_index=True,
    )

    show_diff(source_df=df, modified_df=editor_df, editor_key=st.session_state["enfant_edit"],table_name='t_enfant', key_field='enfant_id')
    return True    

#==================================================================================================
# Calendrier
#==================================================================================================
if "events" not in st.session_state:
    st.session_state.events = None

colors = ["blue", "red", "green"]

events = [
    {
        "title": "Event 1",
        "color": colors[2],
        "location": "LA",
        "start": "2026-07-16 14:00",
        "end": "2026-07-16 16:00",
        "resourceId": "1",
    }
]
people = [
    {"id": "1", "title": "One"},
    {"id": "2", "title": "Two"},
    {"id": "3", "title": "Three"}
]

calendar_display={
        "daygrid":"Day",
        "timegrid":"Time",
        "timeline":"Timeline",
        "resource-daygrid":"Resource: Day",
        "resource-timegrid":"Resource: Time",
        "resource-timeline":"Resource: Timeline",
        "list":"List",
        "multimonth":"Multi months",
}

calendar_options_def = {
    "editable": "true",
    "navLinks": "true",
    "resources": people,
    "selectable": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridDay,dayGridWeek,dayGridMonth",
    },
    "initialDate": "2026-07-16",
    "initialView": "dayGridMonth",
}

calendar_options = { # à supprimer
    "editable": "true",
    "navLinks": "true",
    "resources": people,
    "selectable": "true",
    "headerToolbar": {
        "left": "today prev,next",
        "center": "title",
        "right": "dayGridDay,dayGridWeek,dayGridMonth",
    },
    "initialDate": "2026-07-16",
    "initialView": "dayGridMonth",
}

calendar_css = """
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            font-style: italic;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
        """

def build_calendar():
    global calendar_options, events, calendar_css
    st.session_state.events = events
    cal = calendar(
        events=st.session_state.get("events", events),
        options=calendar_options,
        custom_css=calendar_css,
        key="Calendar",
    )
    return cal

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
    db_table_to_df("t_enfant",True)

def pg_enfant_create():
    st.empty()

def pg_enfant_update():
    st.empty()

def pg_enfant_delete():
    st.empty()
# Resa ============================================================================================
def pg_resa_get():
    df_parent=db_table_to_df("t_parent",True)
    df_enfant=db_table_to_df("t_enfant",True)
    df_resa=db_table_to_df("t_reservation",True)

    df = pd.merge(df_resa, df_enfant, how="left", on=["enfant_id", "enfant_id"])
    df = pd.merge(df, df_parent, how="left", on=["parent_id", "parent_id"])
    df

def pg_resa_create():
    st.empty()

def pg_resa_update():
    st.empty()

def pg_resa_delete():
    st.empty()
#==================================================================================================
def pg_home():
    st.write(db_table_to_df("t_parent",True))
    st.write(db_table_to_df("t_enfant",True))
    st.write(db_table_to_df("t_reservation",True))

def str2time(val):
    ret = datetime.strptime(val, '%d/%m/%Y %H:%M:%S')
    return ret

def str2timedelta(val):
    try:
        ret = datetime.strptime(val, '%d/%m/%Y %H:%M:%S')
    except:
        ret = val
    ret = ret + timedelta(minutes=45)
    return ret

def pg_cal_adm():
    global people,calendar_display,calendar_options_def,calendar_css
    initialDate='2026-07-16'
    calendar_groupby = "level" #"title" #"building"    
    st.title("Planning")

    mode = st.selectbox("Calendar Mode:", options=list(calendar_display.keys()), format_func=lambda x:calendar_display[ x ])
    calendar_options = calendar_options_def
    st.write(f'mode={mode}')
    if "resource" in mode:
        if mode == "resource-daygrid":
            calendar_options = {
                **calendar_options,
                "initialDate": initialDate,
                "initialView": "resourceDayGridDay",
                "firstweekday": 0,
                "resourceGroupField": calendar_groupby,
            }
        elif mode == "resource-timeline":
            calendar_options = {
                **calendar_options,
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "resourceTimelineDay,resourceTimelineWeek,resourceTimelineMonth",
                },
                "initialDate": initialDate,
                "initialView": "resourceTimelineDay",
                "firstweekday": 0,
                "resourceGroupField": calendar_groupby,
            }
        elif mode == "resource-timegrid":
            calendar_options = {
                **calendar_options,
                "initialDate": initialDate,
                "initialView": "resourceTimeGridDay",
                "firstweekday": 0,
                "resourceGroupField": calendar_groupby,
            }
    else:
        if mode == "daygrid":
            calendar_options = {
                **calendar_options,
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "dayGridDay,dayGridWeek,dayGridMonth",
                },
                "initialDate": initialDate,
                "initialView": "dayGridMonth",
                "firstweekday": 0,
            }
        elif mode == "timegrid":
            calendar_options = {
                **calendar_options,
                "initialView": "timeGridWeek",
            }
        elif mode == "timeline":
            calendar_options = {
                **calendar_options,
                "headerToolbar": {
                    "left": "today prev,next",
                    "center": "title",
                    "right": "timelineDay,timelineWeek,timelineMonth",
                },
                "initialDate": initialDate,
                "initialView": "timelineMonth",
            }
        elif mode == "list":
            calendar_options = {
                **calendar_options,
                "initialDate": initialDate,
                "initialView": "listMonth",
            }
        elif mode == "multimonth":
            calendar_options = {
                **calendar_options,
                "initialView": "multiMonthYear",
            }

    df_parent=db_table_to_df("t_parent",True)
    df_enfant=db_table_to_df("t_enfant",True)
    df_resa=db_table_to_df("t_reservation",True)

    df = pd.merge(df_resa, df_enfant, how="left", on=["enfant_id", "enfant_id"])
    df = pd.merge(df, df_parent, how="left", on=["parent_id", "parent_id"])   
    people = df_enfant.copy(deep=True) 
    people=people.rename(columns={'enfant_id':'id','enfant_name':'title'})

    df['start'] = df['resa_date'] + ' ' + df['resa_heure'] + ':00'
    df['start'] = df['start'].map(str2time)
    df['end'] = df['start'].map(str2timedelta)
    df['title'] = df['enfant_name'] + ' ' + str(df['resa_id'])
    dummy={
        "title": "Event 1",
        "color": "colors[2]",
        "location": "LA",
        "start": "2026-07-16 14:00",
        "end": "2026-07-16 16:00",
        "resourceId": "1",
    }
    df=df.rename(columns={
        "enfant_id":"resourceId",
        })
    calendar_events=df.copy(deep=True) 
    calendar_events
    st.session_state.events=calendar_events
    #state = build_calendar()
    state = calendar(
        #events=st.session_state.get("events", events),
        events=calendar_events,
        options=calendar_options,
        custom_css=calendar_css,
        key="Calendar",
    )

def pg_options_adm():
    db=db_get_path()
    subtitle(f'Database: {db}')
    with open(db, "rb") as fp:
        btn = st.download_button(
            label="Download db file",
            data=fp,
            file_name=filenameFull,
            mime="application/octet-stream",
            icon=":material/download:"
        )
    subtitle('Images')
    pic_list()

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
    'User':[
        st.Page(pg_enfant_get, title='Enfant', icon="🚀"),
        st.Page(pg_resa_create, title='Réservation', icon="🧰"),
        st.Page(pg_resa_update, title='Planning enfant', icon="📅"),
    ],
    'Admin': [
        st.Page(pg_parent_adm, title='Gérer parents',icon="🌟"),
        st.Page(pg_enfant_adm, title='Gérer enfants',icon="🧬"),
        st.Page(pg_resa_get, title='Voir réservations',icon="🧬"),
        st.Page(pg_cal_adm, title='Planning prof',icon="📅"),
    ],
    'Options':[    
        st.Page(pg_init_data, title='Init data', icon="🚀"),
        st.Page(pg_options_adm, title='Options',icon="🛠️"),
    ],
}

pg = st.navigation(
    pages if nav_sections else [page for section in pages.values() for page in section],
    position="top" if top_nav else "sidebar"
)
pg.run()
        