import streamlit as st
import pandas as pd
import plotly.express as px
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


load_dotenv()
DB_URL = st.secrets["DATABASE_URL"]

engine = create_engine(DB_URL)



# color palette
blue_palette = ['#1f77b4', '#4c78a8', '#76a5af', '#5fa2ce']

# Page config
st.set_page_config(page_title="Law Firm Dashboard", layout="wide")
st.title("⚖️ Law Firm Insights Dashboard")

# Load data
@st.cache_data(ttl=600)
def load_data():
    query = "SELECT * FROM clean_case_insights;"
    return pd.read_sql(query, engine)

df = load_data()

# Metrics 
col1, col2, col3 = st.columns(3)
col1.metric("Total Cases", len(df))
col2.metric("Overdue Cases", df[df['status'] == 'Overdue'].shape[0])
col3.metric("Total Billable Hours", round(df['total_hours'].fillna(0).sum(), 2))

st.divider()

# Cases per Practice Area
st.subheader("📌 Cases by Practice Area")
area_df = df.groupby('practice_area')['case_id'].count().reset_index(name='total_cases')
fig1 = px.bar(area_df, x='practice_area', y='total_cases',
              color='practice_area', title='Total Cases per Practice Area',
              color_discrete_sequence=blue_palette)
st.plotly_chart(fig1, use_container_width=True)


# Top lawyers
st.subheader("💼 Top 10 Lawyers by Billable Hours")

# Group and sort 
billable_df = (
    df.groupby('lawyer')['total_hours']
    .sum()
    .reset_index()
    .sort_values(by='total_hours', ascending=False)
    .head(10)
)

# bar chart
fig3 = px.bar(
    billable_df,
    x='lawyer',
    y='total_hours',
    color='lawyer',
    title='Top 10 Lawyers by Total Billable Hours',
    color_discrete_sequence=blue_palette
)

st.plotly_chart(fig3, use_container_width=True)


st.subheader("💼 Top 10 Lawyers by Billable Hours")

# filter
status_filter = st.selectbox(
    "Select Case Status:",
    options=["All", "In Progress", "Overdue"],
    index=0
)


if status_filter == "All":
    filtered_df = df.copy()
else:
    filtered_df = df[df['status'] == status_filter]

# Group 
billable_df = (
    filtered_df.groupby('lawyer')['total_hours']
    .sum()
    .reset_index()
    .sort_values(by='total_hours', ascending=False)
    .head(10)
)

# Plot
fig = px.bar(
    billable_df,
    x='lawyer',
    y='total_hours',
    color='lawyer',
    title=f"Top 10 Lawyers by Total Billable Hours ({status_filter} Cases)",
    color_discrete_sequence=blue_palette
)

st.plotly_chart(fig, use_container_width=True)


# Tasks Due in Next 7 Days

st.subheader("📅 Tasks Due in Next 7 Days")

# datetime format
df['latest_due'] = pd.to_datetime(df['latest_due'])

# today's date 
today = date.today()
next_week = today + timedelta(days=7)

# Filter tasks 
upcoming = df[df['latest_due'].dt.date.between(today, next_week)]


st.dataframe(upcoming[['case_id', 'client_name', 'latest_due']], use_container_width=True)

# Cases Ending This Month
st.subheader("📆 Cases Ending This Month")
df['end_date'] = pd.to_datetime(df['end_date'])

# first day of this month and next month
start_of_month = date.today().replace(day=1)
start_of_next_month = (start_of_month + relativedelta(months=1))

# Filter rows 
this_month = df[df['end_date'].dt.date.between(start_of_month, start_of_next_month)]


st.dataframe(this_month[['case_id', 'client_name', 'end_date']], use_container_width=True)

# Average Tasks per Case by Area
st.subheader("🧾 Average Tasks per Case by Practice Area")
avg_tasks = df.groupby('practice_area')['task_count'].mean().round(2).reset_index()
fig6 = px.bar(avg_tasks, x='practice_area', y='task_count',
              title='Average Task Count per Case',
              color='practice_area', color_discrete_sequence=blue_palette)
st.plotly_chart(fig6, use_container_width=True)

# Billed vs Not Billed
st.subheader("💳 Billed vs Not Billed Cases")
billed_count = df['any_billed'].value_counts().reset_index()
billed_count.columns = ['any_billed', 'count']
fig7 = px.pie(billed_count, names='any_billed', values='count',
              title='Billing Status', color_discrete_sequence=blue_palette)
st.plotly_chart(fig7, use_container_width=True)

# Cases with 0 Hours Logged
st.subheader("🚨 Cases with No Logged Hours")
no_hours = df[df['total_hours'].isnull() | (df['total_hours'] == 0)]
st.dataframe(no_hours[['case_id', 'client_name', 'lawyer']], use_container_width=True)


# Full Table
st.subheader("📂 All Case Records")
st.dataframe(df, use_container_width=True)



st.markdown(
    'Built with ❤️ by [Milcah](https://www.linkedin.com/in/milcahmbithi)',
    unsafe_allow_html=True
)


