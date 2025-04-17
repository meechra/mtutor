# student_engagement_dashboard_dummy.py
"""
Dummy Streamlit interface that mimics the workflow of the Student Engagement Analytics Dashboard
for mTutor. It generates synthetic data so the layout, filters, KPIs, and charts can be demonstrated
without connecting to the production ETL pipeline or database.

Run with:
    streamlit run student_engagement_dashboard_dummy.py
"""

from __future__ import annotations

import datetime as dt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Synthetic Data Generator
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_dummy_data(days: int = 90, courses: int = 5, students: int = 400) -> pd.DataFrame:
    """Return a synthetic engagement DataFrame.

    Columns
    -------
    date : datetime (day‑level granularity)
    course : str (Course‑X)
    student_id : int
    session_minutes : float
    quiz_score : float (0‑100)
    completed : bool
    """
    rng = np.random.default_rng(42)
    start_date = dt.date.today() - dt.timedelta(days=days - 1)
    dates = pd.date_range(start=start_date, periods=days, freq="D")
    course_list = [f"Course‑{i + 1}" for i in range(courses)]

    records = []
    for d in dates:
        for c in course_list:
            # sample number of active students for the day & course
            active = rng.integers(low=10, high=students // 3)
            ids = rng.choice(np.arange(students), size=active, replace=False)
            for s in ids:
                session_minutes = rng.uniform(3, 45)
                quiz_score = rng.uniform(40, 100)
                completed = rng.random() < 0.05  # 5 % chance of completion event
                records.append(
                    {
                        "date": d,
                        "course": c,
                        "student_id": int(s),
                        "session_minutes": session_minutes,
                        "quiz_score": quiz_score,
                        "completed": completed,
                    }
                )
    df = pd.DataFrame.from_records(records)
    return df


data = load_dummy_data()

# -----------------------------------------------------------------------------
# 2. Sidebar Filters
# -----------------------------------------------------------------------------
st.sidebar.header("Filters")

min_date, max_date = data["date"].min(), data["date"].max()
from_date = st.sidebar.date_input(
    "From", value=min_date, min_value=min_date, max_value=max_date
)

to_date = st.sidebar.date_input(
    "To", value=max_date, min_value=min_date, max_value=max_date
)

if from_date > to_date:
    st.sidebar.error("'From' date must not be after 'To' date.")

course_options = sorted(data["course"].unique())
selected_courses = st.sidebar.multiselect("Course(s)", course_options, default=course_options)

# Apply filters
filtered = data[(data["date"] >= pd.Timestamp(from_date)) & (data["date"] <= pd.Timestamp(to_date))]
if selected_courses:
    filtered = filtered[filtered["course"].isin(selected_courses)]

# -----------------------------------------------------------------------------
# 3. KPIs
# -----------------------------------------------------------------------------
st.title("📊 Student Engagement Dashboard – Demo")

col1, col2, col3, col4 = st.columns(4)
with col1:
    dau = filtered["student_id"].nunique()
    st.metric("Daily Active Users", f"{dau}")
with col2:
    median_session = filtered["session_minutes"].median()
    st.metric("Median Session (min)", f"{median_session:.1f}")
with col3:
    completion_rate = filtered["completed"].mean() * 100 if not filtered.empty else 0
    st.metric("Completion %", f"{completion_rate:.1f}%")
with col4:
    mean_quiz = filtered["quiz_score"].mean()
    st.metric("Avg Quiz Score", f"{mean_quiz:.1f}")

st.divider()

# -----------------------------------------------------------------------------
# 4. Charts
# -----------------------------------------------------------------------------

# Time‑series of active users
active_daily = (
    filtered.groupby("date")["student_id"]
    .nunique()
    .reset_index(name="active_users")
    .sort_values("date")
)
fig_active = px.line(active_daily, x="date", y="active_users", title="Daily Active Users Over Time")
st.plotly_chart(fig_active, use_container_width=True)

# Box plot of session length by course
fig_session = px.box(
    filtered,
    x="course",
    y="session_minutes",
    title="Session Duration Distribution by Course (min)",
    points="all",
)
st.plotly_chart(fig_session, use_container_width=True)

# Heat‑map: Quiz score vs Session duration buckets
filtered["session_bucket"] = pd.cut(filtered["session_minutes"], bins=[0, 5, 10, 20, 30, 60])
heat = (
    filtered.groupby(["session_bucket"])["quiz_score"]
    .mean()
    .reset_index()
)
heat["session_bucket"] = heat["session_bucket"].astype(str)
fig_heat = px.bar(heat, x="session_bucket", y="quiz_score", title="Avg Quiz Score by Session Length Bucket")
st.plotly_chart(fig_heat, use_container_width=True)

# Sankey placeholder (static example)
st.subheader("Module Progression Flow – Placeholder")
st.markdown("*(Add real Sankey when module sequencing data is available.)*")

# -----------------------------------------------------------------------------
# 5. Footer
# -----------------------------------------------------------------------------
st.caption("Demo dashboard generated with synthetic data. © 2025 mTutor")
