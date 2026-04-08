import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
import sqlite3

# 数据库初始化
def init_db():
    conn = sqlite3.connect("habits.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            daily_goal INTEGER,
            created_at DATE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER,
            record_date DATE,
            count INTEGER DEFAULT 1,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 数据库操作
def add_habit(name, category, goal):
    conn = sqlite3.connect("habits.db")
    c = conn.cursor()
    c.execute("INSERT INTO habits (name, category, daily_goal, created_at) VALUES (?, ?, ?, ?)",
              (name, category, goal, date.today()))
    conn.commit()
    conn.close()

def log_record(habit_id, record_date, count, note):
    conn = sqlite3.connect("habits.db")
    c = conn.cursor()
    c.execute("INSERT INTO records (habit_id, record_date, count, note) VALUES (?, ?, ?, ?)",
              (habit_id, record_date, count, note))
    conn.commit()
    conn.close()

def get_all_habits():
    conn = sqlite3.connect("habits.db")
    df = pd.read_sql("SELECT * FROM habits", conn)
    conn.close()
    return df

def get_habit_records(habit_id):
    conn = sqlite3.connect("habits.db")
    df = pd.read_sql(f"SELECT * FROM records WHERE habit_id = {habit_id}", conn)
    conn.close()
    return df

# 页面设置
st.set_page_config(page_title="习惯追踪器", layout="wide")
st.title("📋 习惯追踪器")

# 侧边栏
with st.sidebar:
    st.subheader("添加新习惯")
    habit_name = st.text_input("习惯名称")
    category = st.selectbox("分类", ["健康", "学习", "工作", "生活", "其他"])
    daily_goal = st.number_input("每日目标次数", min_value=1, value=1)
    if st.button("添加习惯"):
        if habit_name:
            add_habit(habit_name, category, daily_goal)
            st.success("习惯添加成功！")
            st.rerun()

# 主标签页
tab1, tab2, tab3 = st.tabs(["打卡记录", "习惯列表", "数据统计"])

# 打卡记录页
with tab1:
    st.subheader("今日打卡")
    habits = get_all_habits()
    if not habits.empty:
        habit_id = st.selectbox("选择习惯", options=habits["id"].tolist(),
                                format_func=lambda x: habits[habits["id"] == x]["name"].values[0])
        record_date = st.date_input("打卡日期", value=datetime.today())
        count = st.number_input("完成次数", min_value=1, value=1)
        note = st.text_area("备注")
        if st.button("提交打卡"):
            log_record(habit_id, record_date, count, note)
            st.success("打卡成功！")
            st.rerun()
    else:
        st.info("请先在侧边栏添加习惯~")

# 习惯列表页
with tab2:
    st.subheader("所有习惯")
    habits = get_all_habits()
    if not habits.empty:
        st.dataframe(habits[["name", "category", "daily_goal", "created_at"]], use_container_width=True)
    else:
        st.info("还没有添加任何习惯哦")

# 数据统计页
with tab3:
    st.subheader("习惯数据统计")
    habits = get_all_habits()
    if not habits.empty:
        selected_habit_id = st.selectbox("选择习惯查看数据", options=habits["id"].tolist(),
                                         format_func=lambda x: habits[habits["id"] == x]["name"].values[0])
        selected_habit = habits[habits["id"] == selected_habit_id].iloc[0]
        records = get_habit_records(selected_habit_id)
        if not records.empty:
            records["record_date"] = pd.to_datetime(records["record_date"])
            daily_records = records.groupby("record_date")["count"].sum().reset_index()
            daily_records["目标"] = selected_habit["daily_goal"]
            daily_records["完成率"] = (daily_records["count"] / daily_records["目标"] * 100).clip(0, 100)

            # 绘制图表
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(daily_records["record_date"], daily_records["count"], marker="o", label="完成次数")
            ax.axhline(selected_habit["daily_goal"], color="r", linestyle="--", label="目标次数")
            ax.fill_between(daily_records["record_date"], daily_records["count"], daily_records["目标"],
                            where=(daily_records["count"] >= daily_records["目标"]), color="green", alpha=0.3, label="达成目标")
            ax.fill_between(daily_records["record_date"], daily_records["count"], daily_records["目标"],
                            where=(daily_records["count"] < daily_records["目标"]), color="red", alpha=0.3, label="未达成目标")
            ax.set_title(f"{selected_habit['name']} 完成情况")
            ax.tick_params(axis="x", rotation=45)
            ax.legend()
            st.pyplot(fig)
        else:
            st.info("还没有打卡记录，快去打卡吧~")
    else:
        st.info("请先添加习惯")
