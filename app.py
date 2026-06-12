import streamlit as st
import pandas as pd
from datetime import datetime

# --- page config ---
st.set_page_config(
    page_title="Bed-Stuy Community Board 3 Dashboard",
    page_icon="🏘️",
    layout="wide"
)

# --- load data ---
@st.cache_data
def load_data():
    df = pd.read_csv("data/cb3_meetings.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# --- header ---
st.title("🏘️ Bed-Stuy Community Board 3")
st.markdown("Track meetings, filter by topic, and stay informed about what's happening in your community.")

# --- sidebar filters ---
st.sidebar.header("Filter Meetings")

topics = ["All"] + sorted(df["topic"].unique().tolist())
selected_topic = st.sidebar.selectbox("Topic", topics)

years = ["All"] + sorted(df["date"].dt.year.unique().tolist(), reverse=True)
selected_year = st.sidebar.selectbox("Year", years)

show_upcoming = st.sidebar.checkbox("Upcoming meetings only", value=True)

# --- filter logic ---
filtered = df.copy()

if selected_topic != "All":
    filtered = filtered[filtered["topic"] == selected_topic]

if selected_year != "All":
    filtered = filtered[filtered["date"].dt.year == int(selected_year)]

if show_upcoming:
    filtered = filtered[filtered["date"] >= datetime.now()]

filtered = filtered.sort_values("date", ascending=True)

# --- metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Meetings shown", len(filtered))
col2.metric("Topics covered", filtered["topic"].nunique())
col3.metric("Date range", f"{filtered['date'].dt.year.min() if len(filtered) > 0 else 'N/A'} - {filtered['date'].dt.year.max() if len(filtered) > 0 else 'N/A'}")

st.divider()

# --- meeting list ---
if len(filtered) == 0:
    st.info("No meetings found for the selected filters.")
else:
    for _, row in filtered.iterrows():
        with st.expander(f"📅 {row['date'].strftime('%B %d, %Y %I:%M %p')} — {row['title']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Topic:** {row['topic']}")
                st.markdown(f"**Location:** {row['location'] if row['location'] else 'TBD'}")
            with col2:
                if pd.notna(row.get("agenda_url")) and row["agenda_url"] != "None":
                    st.markdown(f"[📄 View Agenda]({row['agenda_url']})")
                if pd.notna(row["description"]) and str(row["description"]).strip() != "nan":
                    st.markdown(f"**Notes:** {str(row['description'])[:300]}")