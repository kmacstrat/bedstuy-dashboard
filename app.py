import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from icalendar import Calendar, Event
from io import BytesIO

st.set_page_config(
    page_title="Bed-Stuy Neighborhood Dashboard",
    page_icon="🏘️",
    layout="wide"
)

@st.cache_data
def load_meetings():
    df = pd.read_csv("data/cb3_meetings.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["type"] = "Meeting"
    return df

@st.cache_data
def load_permits():
    df = pd.read_csv("data/permits.csv")
    df["date"] = pd.to_datetime(df["filing_date"])
    df = df.dropna(subset=["date"])
    df["type"] = "Permit"
    df["title"] = df["job_type_label"] + " — " + df["address"]
    df["topic"] = df["job_type_label"]
    return df

meetings = load_meetings()
permits = load_permits()

def calendar_button(row, key):
    cal = Calendar()
    cal.add("prodid", "-//Bed-Stuy Dashboard//EN")
    cal.add("version", "2.0")
    event = Event()
    event.add("summary", row["title"])
    event.add("dtstart", row["date"].to_pydatetime())
    event.add("dtend", row["date"].to_pydatetime())
    if pd.notna(row.get("location")):
        event.add("location", str(row["location"]))
    cal.add_component(event)
    ics_bytes = BytesIO(cal.to_ical())
    st.download_button(
        label="📆 Add to Calendar",
        data=ics_bytes,
        file_name=f"meeting_{row['date'].strftime('%Y%m%d')}.ics",
        mime="text/calendar",
        key=key
    )

st.title("🏘️ Bed-Stuy Neighborhood Dashboard")
st.markdown("Track development permits and community board meetings in one place.")

tab1, tab2, tab3 = st.tabs(["📅 Timeline", "🏛️ CB3 Meetings", "🏗️ Permits"])

with tab1:
    st.subheader("Unified Timeline")
    st.markdown("Permits and CB3 meetings together — spot the patterns.")

    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("From", value=datetime(2024, 9, 1))
    with col2:
        end_date = st.date_input("To", value=datetime.now())
    with col3:
        show_type = st.multiselect(
            "Show",
            ["Meeting", "Permit"],
            default=["Meeting", "Permit"]
        )

    llc_only = st.checkbox("Show LLC-owned permits only")

    m = meetings.copy()
    p = permits.copy()

    for col in ["address", "owner", "is_llc", "job_type_label", "permit_status", "residential"]:
        if col not in m.columns:
            m[col] = None
    for col in ["location", "description", "agenda_url"]:
        if col not in p.columns:
            p[col] = None

    keep_cols = ["date", "title", "topic", "type", "location", "description",
                 "agenda_url", "address", "owner", "is_llc", "job_type_label",
                 "permit_status", "residential"]

    timeline = pd.concat([m[keep_cols], p[keep_cols]], ignore_index=True)
    timeline = timeline[
        (timeline["date"] >= pd.Timestamp(start_date)) &
        (timeline["date"] <= pd.Timestamp(end_date)) &
        (timeline["type"].isin(show_type))
    ]

    if llc_only:
        timeline = timeline[
            (timeline["type"] == "Meeting") |
            (timeline["is_llc"] == True)
        ]

    timeline = timeline.sort_values("date", ascending=False).reset_index(drop=True)

    st.markdown("### Activity Over Time")
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Annual", "Monthly", "Permit vs Meeting Overlap"])

with chart_tab1:
    annual = timeline.copy()
    annual["year"] = annual["date"].dt.year.astype(str)
    annual_grouped = (
        annual.groupby(["year", "type"])
        .size()
        .reset_index(name="count")
    )
    annual_grouped["display_count"] = annual_grouped.apply(
        lambda r: r["count"] * 10 if r["type"] == "Meeting" else r["count"],
        axis=1
    )
    fig = px.bar(
        annual_grouped,
        x="year",
        y="display_count",
        color="type",
        barmode="group",
        color_discrete_map={"Meeting": "#4a7c59", "Permit": "#9b8ec4"},
        labels={"display_count": "Count", "year": "Year", "type": ""},
        title="Annual Activity (meetings scaled div by 100 for visibility)"
    )
    st.plotly_chart(fig, use_container_width=True)

with chart_tab2:
    monthly = timeline.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    monthly_grouped = (
        monthly.groupby(["month", "type"])
        .size()
        .reset_index(name="count")
    )
    monthly_grouped["display_count"] = monthly_grouped.apply(
        lambda r: r["count"] // 100 if r["type"] == "Permit" else r["count"],
        axis=1
    )
    fig = px.bar(
        monthly_grouped,
        x="month",
        y="display_count",
        color="type",
        barmode="group",
        color_discrete_map={"Meeting": "#4a7c59", "Permit": "#9b8ec4"},
        labels={"display_count": "Count", "month": "Month", "type": ""},
        title="Monthly Activity (permits scaled ÷100 for visibility)"
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

    with chart_tab3:
        st.markdown("**Months where both permit filings and CB meetings occurred**")
        overlap = timeline.copy()
        overlap["month"] = overlap["date"].dt.to_period("M").astype(str)
        overlap_grouped = (
            overlap.groupby(["month", "type"])
            .size()
            .reset_index(name="count")
        )
        pivot = overlap_grouped.pivot(index="month", columns="type", values="count").fillna(0)
        if "Meeting" in pivot.columns and "Permit" in pivot.columns:
            pivot = pivot[
                (pivot["Meeting"] > 0) & (pivot["Permit"] > 0)
            ].reset_index()
            overlap_melted = pivot.melt(id_vars="month", var_name="type", value_name="count")
            overlap_melted["display_count"] = overlap_melted.apply(
                lambda r: r["count"] // 100 if r["type"] == "Permit" else r["count"],
                axis=1
            )
            fig = px.bar(
                overlap_melted,
                x="month",
                y="display_count",
                color="type",
                barmode="group",
                color_discrete_map={"Meeting": "#4a7c59", "Permit": "#9b8ec4"},
                labels={"display_count": "Count", "month": "Month", "type": ""},
                title="Months with Both Permits and Meetings (permits scaled ÷100)"
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No overlapping months found in the selected date range.")

        st.divider()
        st.markdown(f"### {len(timeline)} items in range")

    for idx, row in timeline.iterrows():
        is_meeting = row["type"] == "Meeting"
        label = "MEETING" if is_meeting else "PERMIT"
        color = "🟩" if is_meeting else "🟪"

        with st.expander(f"{color} {row['date'].strftime('%b %d, %Y')} | {label} | {row['title']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Type:** {label}")
                st.markdown(f"**Date:** {row['date'].strftime('%B %d, %Y')}")
                if is_meeting:
                    st.markdown(f"**Topic:** {row['topic']}")
                    location = row['location'] if pd.notna(row.get('location')) else 'TBD'
                    st.markdown(f"**Location:** {location}")
                else:
                    st.markdown(f"**Permit type:** {row['job_type_label']}")
                    st.markdown(f"**Address:** {row['address']}")
                    st.markdown(f"**Status:** {row['permit_status']}")
            with col2:
                if not is_meeting:
                    st.markdown(f"**Owner:** {row['owner']}")
                    if pd.notna(row.get('is_llc')) and row['is_llc']:
                        st.markdown("⚠️ **LLC owned**")
                    st.markdown(f"**Residential:** {row['residential']}")
                if is_meeting:
                    if pd.notna(row.get("agenda_url")) and str(row["agenda_url"]) != "None":
                        st.markdown(f"[📄 View Agenda]({row['agenda_url']})")
                    if pd.notna(row.get("description")) and str(row.get("description", "")).strip() not in ["nan", ""]:
                        st.markdown(f"**Notes:** {str(row['description'])[:300]}")
                    calendar_button(row, key=f"tl_{idx}")

with tab2:
    st.subheader("CB3 Community Board Meetings")

    topics = ["All"] + sorted(meetings["topic"].unique().tolist())
    selected_topic = st.selectbox("Filter by topic", topics)
    years = ["All"] + sorted(meetings["date"].dt.year.unique().tolist(), reverse=True)
    selected_year = st.selectbox("Filter by year", years)
    upcoming_only = st.checkbox("Upcoming meetings only", value=True)

    filtered = meetings.copy()
    if selected_topic != "All":
        filtered = filtered[filtered["topic"] == selected_topic]
    if selected_year != "All":
        filtered = filtered[filtered["date"].dt.year == int(selected_year)]
    if upcoming_only:
        filtered = filtered[filtered["date"] >= datetime.now()]
    filtered = filtered.sort_values("date", ascending=True).reset_index(drop=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Meetings", len(filtered))
    col2.metric("Topics", filtered["topic"].nunique())
    col3.metric("Date range",
        f"{filtered['date'].dt.year.min() if len(filtered) > 0 else 'N/A'} - "
        f"{filtered['date'].dt.year.max() if len(filtered) > 0 else 'N/A'}"
    )

    st.divider()

    for idx, row in filtered.iterrows():
        with st.expander(
            f"📅 {row['date'].strftime('%B %d, %Y %I:%M %p')} — {row['title']}"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Topic:** {row['topic']}")
                location = row['location'] if pd.notna(row.get('location')) else 'TBD'
                st.markdown(f"**Location:** {location}")
            with col2:
                if pd.notna(row.get("agenda_url")) and str(row["agenda_url"]) != "None":
                    st.markdown(f"[📄 View Agenda]({row['agenda_url']})")
                if pd.notna(row.get("description")) and str(row.get("description", "")).strip() not in ["nan", ""]:
                    st.markdown(f"**Notes:** {str(row['description'])[:300]}")
                calendar_button(row, key=f"m_{idx}")

with tab3:
    st.subheader("Building Permits")
    st.markdown("Development activity across Bed-Stuy zip codes.")

    col1, col2, col3 = st.columns(3)
    with col1:
        job_types = ["All"] + sorted(permits["job_type_label"].dropna().unique().tolist())
        selected_job = st.selectbox("Permit type", job_types)
    with col2:
        res_filter = st.selectbox("Residential", ["All", "Yes", "No"])
    with col3:
        llc_filter = st.checkbox("LLC owned only", key="llc_tab3")

    filtered_permits = permits.copy()
    if selected_job != "All":
        filtered_permits = filtered_permits[filtered_permits["job_type_label"] == selected_job]
    if res_filter != "All":
        filtered_permits = filtered_permits[filtered_permits["residential"] == res_filter]
    if llc_filter:
        filtered_permits = filtered_permits[filtered_permits["is_llc"] == True]

    filtered_permits = filtered_permits.sort_values("date", ascending=False).reset_index(drop=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Permits", len(filtered_permits))
    col2.metric("LLC owned", int(filtered_permits["is_llc"].sum()))
    col3.metric("New buildings", int((filtered_permits["job_type"] == "NB").sum()))

    st.divider()

    for idx, row in filtered_permits.iterrows():
        with st.expander(
            f"🏗️ {row['date'].strftime('%b %d, %Y')} — {row['title']}"
        ):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Address:** {row['address']}")
                st.markdown(f"**Permit type:** {row['job_type_label']}")
                st.markdown(f"**Status:** {row['permit_status']}")
                st.markdown(f"**Residential:** {row['residential']}")
            with col2:
                st.markdown(f"**Owner:** {row['owner']}")
                if pd.notna(row.get('is_llc')) and row['is_llc']:
                    st.markdown("⚠️ **LLC owned**")
                st.markdown(f"**Council district:** {row['gis_council_district']}")