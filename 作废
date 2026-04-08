import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# --- 数据库初始化 ---
def init_db():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        goal INTEGER,
        created_at DATE DEFAULT CURRENT_DATE
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER,
        date DATE,
        count INTEGER DEFAULT 1,
        note TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id)
    )''')
    conn.commit()
    conn.close()

init_db()

# --- 数据库操作 ---
def add_habit(name, category, goal):
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("INSERT INTO habits (name, category, goal) VALUES (?, ?, ?)", (name, category, goal))
    conn.commit()
    conn.close()

def log_record(habit_id, date, count, note):
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("INSERT INTO records (habit_id, date, count, note) VALUES (?, ?, ?, ?)", (habit_id, date, count, note))
    conn.commit()
    conn.close()

def get_all_habits():
    conn = sqlite3.connect('habits.db')
    df = pd.read_sql("SELECT * FROM habits", conn)
    conn.close()
    return df

def get_records_by_habit(habit_id):
    conn = sqlite3.connect('habits.db')
    df = pd.read_sql(f"SELECT * FROM records WHERE habit_id = {habit_id}", conn)
    conn.close()
    return df

# --- 页面设置 ---
st.set_page_config(page_title="Habit Tracker", layout="wide")
st.title("📋 Habit Tracker")

# --- 侧边栏 ---
with st.sidebar:
    st.header("Manage Habits")
    habit_name = st.text_input("Habit Name")
    category = st.selectbox("Category", ["Health", "Study", "Work", "Life", "Other"])
    goal = st.number_input("Daily Goal", min_value=1, value=1)
    if st.button("Add Habit"):
        if habit_name:
            add_habit(habit_name, category, goal)
            st.success("Habit added!")
            st.experimental_rerun()

# --- 主页面 ---
tab1, tab2, tab3 = st.tabs(["Log Habit", "All Habits", "Stats"])

with tab1:
    st.header("Log Habit")
    habits = get_all_habits()
    if not habits.empty:
        habit_id = st.selectbox("Select Habit", options=habits['id'].tolist(), format_func=lambda x: habits[habits['id'] == x]['name'].values[0])
        date = st.date_input("Date", datetime.now())
        count = st.number_input("Completed Count", min_value=1, value=1)
        note = st.text_area("Notes")
        if st.button("Submit Log"):
            log_record(habit_id, date, count, note)
            st.success("Logged successfully!")
            st.experimental_rerun()
    else:
        st.info("Add a habit first in the sidebar!")

with tab2:
    st.header("All Habits")
    habits = get_all_habits()
    if not habits.empty:
        st.dataframe(habits[['name', 'category', 'goal', 'created_at']])
    else:
        st.info("No habits added yet.")

with tab3:
    st.header("Habit Stats")
    habits = get_all_habits()
    if not habits.empty:
        selected_habit = st.selectbox("View Habit Stats", options=habits['id'].tolist(), format_func=lambda x: habits[habits['id'] == x]['name'].values[0])
        habit_data = habits[habits['id'] == selected_habit].iloc[0]
        records = get_records_by_habit(selected_habit)
        if not records.empty:
            records['date'] = pd.to_datetime(records['date'])
            records = records.sort_values('date')
            daily = records.groupby('date')['count'].sum().reset_index()
            daily['goal'] = habit_data['goal']
            daily['Progress'] = (daily['count'] / daily['goal'] * 100).clip(0, 100)
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(daily['date'], daily['count'], marker='o', label='Completed')
            ax.axhline(y=habit_data['goal'], color='r', linestyle='--', label='Goal')
            ax.fill_between(daily['date'], daily['count'], daily['goal'], where=(daily['count'] >= daily['goal']), color='green', alpha=0.3)
            ax.fill_between(daily['date'], daily['count'], daily['goal'], where=(daily['count'] < daily['goal']), color='red', alpha=0.3)
            ax.set_title(f"{habit_data['name']} Progress")
            ax.legend()
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("No logs yet.")
    else:
        st.info("Add a habit first!")
