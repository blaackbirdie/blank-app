import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

PASSWORD = "u2dWpHuiqJUhLG4b"

def check_password():
    if "auth" not in st.session_state:
        st.session_state.auth = False

    if not st.session_state.auth:
        st.title("🔐 Вход в дашборд")
        pwd = st.text_input("Пароль", type="password")

        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        elif pwd:
            st.error("Неверный пароль")

        return False

    return True


if not check_password():
    st.stop()


@st.cache_data
def load_data():
    np.random.seed(42)

    users = ["Аня", "Борис", "Катя", "Дима"]
    projects = ["Проект A", "Проект B", "Проект C", "Проект D"]

    data = []

    for _ in range(400):
        data.append({
            "user_name": np.random.choice(users),
            "project": np.random.choice(projects),
            "task_name": f"Задача {np.random.randint(1, 25)}",
            "date": pd.Timestamp("2026-04-01") + pd.to_timedelta(np.random.randint(0, 90), unit="d"),
            "hours": round(np.random.uniform(0.5, 6), 2)
        })

    return pd.DataFrame(data)


df = load_data()


st.title("📊 Дашборд по времени работы")

col1, col2, col3 = st.columns(3)

with col1:
    date_from = st.date_input("Дата с", value=None)

with col2:
    date_to = st.date_input("Дата по", value=None)

with col3:
    selected_users = st.multiselect(
        "Сотрудники",
        options=sorted(df["user_name"].unique())
    )



filtered = df.copy()

if date_from:
    filtered = filtered[filtered["date"] >= pd.to_datetime(date_from)]

if date_to:
    filtered = filtered[filtered["date"] <= pd.to_datetime(date_to)]

if selected_users:
    filtered = filtered[filtered["user_name"].isin(selected_users)]


col1, col2 = st.columns(2)

with col1:
    st.metric("Всего часов", round(filtered["hours"].sum(), 1))

with col2:
    st.metric("Количество сотрудников", filtered["user_name"].nunique())


st.divider()



st.subheader("👥 Время по сотрудникам")

users_summary = (
    filtered.groupby("user_name")["hours"]
    .sum()
    .reset_index()
    .sort_values("hours", ascending=False)
)

chart_users = alt.Chart(users_summary).mark_bar().encode(
    x=alt.X("hours:Q", title="Часы"),
    y=alt.Y("user_name:N", sort="-x", title="Сотрудник"),
    tooltip=["user_name", "hours"]
)

st.altair_chart(chart_users, use_container_width=True)

st.dataframe(users_summary, use_container_width=True)



st.divider()
st.subheader("🔍 Детализация по сотруднику")

selected_user = st.selectbox(
    "Выберите сотрудника",
    options=users_summary["user_name"].tolist() if not users_summary.empty else []
)

if selected_user:
    user_df = filtered[filtered["user_name"] == selected_user]

    st.markdown(f"### 👤 {selected_user}")

    # 📁 проекты
    proj_summary = (
        user_df.groupby("project")["hours"]
        .sum()
        .reset_index()
        .sort_values("hours", ascending=False)
    )

    st.write("### 📁 Проекты")

    chart_proj = alt.Chart(proj_summary).mark_bar().encode(
        x=alt.X("hours:Q", title="Часы"),
        y=alt.Y("project:N", sort="-x", title="Проект"),
        tooltip=["project", "hours"]
    )

    st.altair_chart(chart_proj, use_container_width=True)

    st.dataframe(proj_summary, use_container_width=True)


    st.write("### 📋 Задачи")

    task_summary = (
        user_df.groupby("task_name")["hours"]
        .sum()
        .reset_index()
        .sort_values("hours", ascending=False)
    )

    st.dataframe(task_summary, use_container_width=True)