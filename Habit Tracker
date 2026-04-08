import streamlit as st
import sqlite3
import pandas as pd
import datetime
import calmap
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import timedelta

st.set_page_config(page_title="习惯追踪器·全能版", layout="wide")
st.title("📅 习惯追踪器 · 全能版")

def init_db():
    conn = sqlite3.connect('habit_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS habits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL,
                  category TEXT DEFAULT '其他',
                  cycle_type TEXT DEFAULT 'weekly',
                  cycle_goal INTEGER DEFAULT 3,
                  create_time DATE DEFAULT (DATE('now')))''')
    c.execute('''CREATE TABLE IF NOT EXISTS records
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  habit_id INTEGER,
                  record_date DATE NOT NULL,
                  note TEXT,
                  is_complete INTEGER DEFAULT 1,
                  FOREIGN KEY (habit_id) REFERENCES habits(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS achievements
                 (habit_id INTEGER,
                  cycle_key TEXT NOT NULL,
                  achieved INTEGER DEFAULT 1,
                  achieved_date DATE,
                  UNIQUE(habit_id, cycle_key))''')
    conn.commit()
    conn.close()

init_db()

def get_all_habits():
    conn = sqlite3.connect('habit_data.db')
    df = pd.read_sql('SELECT * FROM habits', conn)
    conn.close()
    return df

def add_habit(name, category, cycle_type, cycle_goal):
    try:
        conn = sqlite3.connect('habit_data.db')
        c = conn.cursor()
        c.execute('INSERT INTO habits (name, category, cycle_type, cycle_goal) VALUES (?,?,?,?)',
                  (name, category, cycle_type, cycle_goal))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def update_habit(hid, category, cycle_type, cycle_goal):
    conn = sqlite3.connect('habit_data.db')
    c = conn.cursor()
    c.execute('UPDATE habits SET category=?, cycle_type=?, cycle_goal=? WHERE id=?',
              (category, cycle_type, cycle_goal, hid))
    conn.commit()
    conn.close()

def delete_habit(hid):
    conn = sqlite3.connect('habit_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM records WHERE habit_id=?', (hid,))
    c.execute('DELETE FROM achievements WHERE habit_id=?', (hid,))
    c.execute('DELETE FROM habits WHERE id=?', (hid,))
    conn.commit()
    conn.close()

def get_habit_records(hid):
    conn = sqlite3.connect('habit_data.db')
    df = pd.read_sql('SELECT * FROM records WHERE habit_id=? ORDER BY record_date', conn, params=(hid,))
    conn.close()
    if not df.empty:
        df['record_date'] = pd.to_datetime(df['record_date'])
    return df

def check_habit_with_note(hid, date, note):
    conn = sqlite3.connect('habit_data.db')
    c = conn.cursor()
    c.execute('SELECT * FROM records WHERE habit_id=? AND record_date=?', (hid, date))
    exist = c.fetchone()
    if exist:
        c.execute('UPDATE records SET note=? WHERE habit_id=? AND record_date=?', (note, hid, date))
    else:
        c.execute('INSERT INTO records (habit_id, record_date, note) VALUES (?,?,?)', (hid, date, note))
    conn.commit()
    conn.close()

def uncheck_habit(hid, date):
    conn = sqlite3.connect('habit_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM records WHERE habit_id=? AND record_date=?', (hid, date))
    conn.commit()
    conn.close()

def get_current_cycle(cycle_type):
    today = datetime.date.today()
    if cycle_type == 'daily':
        s = today
        e = today
        key = f'daily_{today}'
    elif cycle_type == 'weekly':
        s = today - timedelta(days=today.weekday())
        e = s + timedelta(days=6)
        key = f'weekly_{s}_{e}'
    else:
        s = today.replace(day=1)
        nm = today.replace(day=28) + timedelta(days=4)
        e = nm - timedelta(days=nm.day)
        key = f'monthly_{s.year}_{s.month}'
    return s, e, key

def get_cycle_progress(hid, cycle_type, goal):
    s, e, _ = get_current_cycle(cycle_type)
    df = get_habit_records(hid)
    if df.empty:
        return 0, False, 0, (e - datetime.date.today()).days + 1
    mask = (df.record_date.dt.date >= s) & (df.record_date.dt.date <= e)
    cnt = len(df[mask])
    left_days = (e - datetime.date.today()).days + 1
    achieved = cnt >= goal
    pct = min(cnt/goal*100, 
