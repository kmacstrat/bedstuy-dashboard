import requests
from icalendar import Calendar
from datetime import datetime
import pandas as pd

ICAL_URL = "https://calendar.google.com/calendar/ical/bk03%40cb.nyc.gov/public/basic.ics"

# Map keywords in title to topic tags
TOPIC_TAGS = {
    "Housing & Land Use": "Housing",
    "Economic Development": "Economic Development",
    "Transportation": "Transportation",
    "Education": "Education",
    "Health": "Health",
    "Senior Services": "Seniors",
    "Veterans": "Veterans",
    "Parks": "Parks & Culture",
    "Civic & Public Safety": "Public Safety",
    "Landmarks": "Landmarks",
    "Cannabis": "Cannabis",
    "Budget": "Budget",
    "Gun Violence": "Public Safety",
}

def tag_meeting(title):
    for keyword, tag in TOPIC_TAGS.items():
        if keyword.lower() in title.lower():
            return tag
    return "General"

def fetch_cb3_meetings():
    response = requests.get(ICAL_URL)
    cal = Calendar.from_ical(response.text)
    
    meetings = []
    for component in cal.walk():
        if component.name == "VEVENT":
            dtstart = component.get("DTSTART")
            date = dtstart.dt if dtstart else None
            if hasattr(date, 'hour'):
                date = date.replace(tzinfo=None)
            else:
                date = datetime(date.year, date.month, date.day)

            attach = component.get("ATTACH")
            agenda_url = str(attach) if attach else None
            description = str(component.get("DESCRIPTION", ""))
            title = str(component.get("SUMMARY", ""))
            location = str(component.get("LOCATION", ""))

            # skip holds, cancelled, holidays, and office closures
            skip_keywords = ["[hold]", "cancelled", "holiday", "office closed"]
            if any(kw in title.lower() for kw in skip_keywords):
                continue

            meetings.append({
                "title": title,
                "date": date,
                "location": location,
                "description": description,
                "agenda_url": agenda_url,
                "topic": tag_meeting(title),
            })
    
    df = pd.DataFrame(meetings)
    df = df.sort_values("date", ascending=False)
    df = df.drop_duplicates(subset=["title", "date"])
    
    # save to CSV for use in the dashboard
    df.to_csv("data/cb3_meetings.csv", index=False)
    print(f"Saved {len(df)} meetings to data/cb3_meetings.csv")
    return df

fetch_cb3_meetings()