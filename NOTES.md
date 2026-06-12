# Project Notes & Feature Ideas

## Known Data Gaps

- CB3 agendas incomplete (only 7 in 2025, missing months)
- About section outdated (budget priorities only through FY2019)
- No real-time attendance or RSVP mechanism on CB site

## Feature Ideas

- Attendance submission form that notifies the board directly
- Alert/subscription system for meetings by topic tag
- Expand demographics layer using DCP Community District Profiles
- Cross-reference development permits with board meeting agendas
- Hardware store / small business access layer (commercial displacement data)
- Scale to all 59 NYC community districts
- Add a banner on the dashboard that says "Don't see an upcoming meeting? CB3 typically posts 2-4 weeks in advance -- check back soon" so users understand it's a data gap, not a tool gap
- cron job to pull ical feed weekly

## Data Sources Found

- Google Calendar iCal feed: src=YmswM0BjYi5ueWMuZ292 (CB3)
- NYC DCP Community District Profiles: [communityprofiles.planning.nyc.gov](http://communityprofiles.planning.nyc.gov)
- NYCDB: github.com/nycdb/nycdb
- NYC Open Data: Residential Projects dataset

## Questions to Resolve

- Are other CB's calendar feeds structured the same way?
- How messy are the agenda PDFs -- are they parseable?
- 

## Big Vision Features

### Elected Official Accountability Layer

- Tie permit approvals and CB votes to assembly members, city council 

  members, and district reps

- Show voting records alongside stated policy positions

- Election-time story: who showed up, who voted what, who benefits

- Data sources to research: NYC Council voting records, state legislature 

  votes, campaign finance data (follow the money angle)

- Could be its own tab: "Your Representatives"

### Mobile / App

- Make Streamlit layout mobile-responsive as near-term fix

- Longer term: convert to a proper mobile app (React Native or PWA)

- Push notifications for upcoming meetings would be killer on mobile

  ("Housing & Land Use meeting tomorrow -- a developer just filed permits 

  on your block")

