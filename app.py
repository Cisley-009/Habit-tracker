import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
from io import BytesIO

st.set_page_config(page_title="习惯追踪", layout="wide")
st.title("📘 高级习惯追踪器")

# ======================
# 初始化数据
# ======================
if "habits" not in st.session_state:
    st.session_state.habits = []
if "records" not in st.session_state:
    st.session_state.records = []
if "streak_cache" not in st.session_state:
    st.session_state.streak_cache = {}

# ======================
# 1. 添加习惯（含自定义周期）
# ======================
with st.sidebar:
    st.subheader("➕ 新建习惯")
    name = st.text_input("习惯名称")
    category = st.selectbox("分类", ["健身", "阅读", "学习", "生活", "其他"])
    freq_type = st.radio("周期类型", ["每周", "每月"], horizontal=True)
    target = st.number_input(f"{freq_type}目标次数", min_value=1, value=3)
    if st.button("保存习惯") and name:
        hid = len(st.session_state.habits) + 1
        st.session_state.habits.append({
            "id": hid,
            "name": name,
            "category": category,
            "freq": freq_type,
            "target": target
        })
        st.success("已创建")

# ======================
# 2. 打卡（带备注：内容/时长/体重）
# ======================
tab1, tab2, tab3, tab4 = st.tabs(["打卡", "统计", "图表", "导出"])

with tab1:
    st.subheader("今日打卡")
    if not st.session_state.habits:
        st.info("请先添加习惯")
    else:
        habit_map = {h["name"]: h["id"] for h in st.session_state.habits}
        hname = st.selectbox("选择习惯", list(habit_map.keys()))
        hid = habit_map[hname]
        today = st.date_input("日期")
        note = st.text_area("备注（内容/时长/体重）")
        if st.button("✅ 确认打卡"):
            st.session_state.records.append({
                "hid": hid,
                "date": str(today),
                "note": note,
                "ts": datetime.now().timestamp()
            })
            st.success("打卡成功！")
            # 气球奖励
            st.balloons()

# ======================
# 3. 连续天数 / 最长连续 / 成就
# ======================
with tab2:
    st.subheader("成就统计")
    if not st.session_state.habits:
        st.info("暂无习惯")
    else:
        hname = st.selectbox("查看习惯", list(habit_map.keys()))
        hid = habit_map[hname]
        recs = [r for r in st.session_state.records if r["hid"] == hid]

        if recs:
            df = pd.DataFrame(recs)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")
            dates = df["date"].dt.date.unique()
            dates.sort()

            # 连续计算
            current = 1
            max_s = 1
            for i in range(1, len(dates)):
                if dates[i] == dates[i-1] + timedelta(days=1):
                    current +=1
                    max_s = max(max_s, current)
                else:
                    current =1

            st.metric("今日连续天数", current)
            st.metric("历史最长连续", max_s)
        else:
            st.info("暂无打卡")

# ======================
# 4. 图表：年热力图 / 月视图 / 周视图 / 折线图
# ======================
with tab3:
    st.subheader("数据可视化")
    if st.session_state.habits and st.session_state.records:
        hname = st.selectbox("选择习惯", list(habit_map.keys()), key="chart_h")
        hid = habit_map[hname]
        recs = [r for r in st.session_state.records if r["hid"] == hid]
        if recs:
            df = pd.DataFrame(recs)
            df["date"] = pd.to_datetime(df["date"])
            df["day"] = df["date"].dt.date
            daily = df.groupby("day").size()

            view = st.radio("视图", ["折线图", "周视图", "月视图"], horizontal=True)
            if view == "折线图":
                st.line_chart(daily)
            elif view == "周视图":
                df["weekday"] = df["date"].dt.dayofweek
                st.bar_chart(df.groupby("weekday").size())
            elif view == "月视图":
                df["month"] = df["date"].dt.month
                st.bar_chart(df.groupby("month").size())
        else:
            st.info("无数据")
    else:
        st.info("请先打卡")

# ======================
# 5. 导出 Excel
# ======================
with tab4:
    st.subheader("导出Excel")
    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as w:
            df.to_excel(w, index=False)
        st.download_button("下载记录", output.getvalue(), "habit_records.xlsx")
    else:
        st.info("无记录可导出")

# ======================
# 6. 周期快结束智能提醒
# ======================
st.divider()
st.subheader("⏰ 周期提醒")
for h in st.session_state.habits:
    hid = h["id"]
    cnt = sum(1 for r in st.session_state.records if r["hid"] == hid)
    need = h["target"] - cnt
    if need > 0:
        st.warning(f"{h['name']} | {h['freq']}需完成{h['target']}次，还差{need}次")
    else:
        st.success(f"{h['name']} | 已完成目标🎉")
