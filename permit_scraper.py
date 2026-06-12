import requests
import pandas as pd

BEDSTUY_ZIPS = ["11205", "11206", "11216", "11221", "11233"]

JOB_TYPE_LABELS = {
    "NB": "New Building",
    "A1": "Major Alteration",
    "A2": "Minor Alteration",
    "DM": "Demolition",
    "A3": "Minor Alteration (A3)",
}

PERMIT_TYPE_LABELS = {
    "NB": "New Building",
    "AL": "Alteration",
    "EW": "Equipment Work",
    "FO": "Foundation",
    "SG": "Sign",
    "BL": "Boiler",
    "MH": "Mechanical",
    "PL": "Plumbing",
}

def fetch_permits_for_zip(zip_code, limit=1000):
    url = (
        f"https://data.cityofnewyork.us/resource/ipu4-2q9a.json"
        f"?zip_code={zip_code}&$limit={limit}"
        f"&$order=filing_date DESC"
    )
    response = requests.get(url)
    return response.json()

def fetch_all_permits():
    all_permits = []
    
    for zip_code in BEDSTUY_ZIPS:
        print(f"Fetching permits for {zip_code}...")
        permits = fetch_permits_for_zip(zip_code)
        all_permits.extend(permits)
        print(f"  Got {len(permits)} permits")
    
    df = pd.DataFrame(all_permits)
    
    df["filing_date"] = pd.to_datetime(df["filing_date"], errors="coerce")
    df["job_type_label"] = df["job_type"].map(JOB_TYPE_LABELS).fillna(df["job_type"])
    df["permit_type_label"] = df["permit_type"].map(PERMIT_TYPE_LABELS).fillna(df["permit_type"])
    
    df["owner"] = df.apply(
        lambda r: r.get("owner_s_business_name", "")
        if r.get("owner_s_business_name") not in ["N/A", "", None]
        else f"{r.get('owner_s_first_name', '')} {r.get('owner_s_last_name', '')}".strip(),
        axis=1
    )

    df["address"] = (
        df["house__"].astype(str) + " " + 
        df["street_name"].astype(str) + 
        ", Brooklyn NY " + 
        df["zip_code"].astype(str)
    )

    df["is_llc"] = df["owner_s_business_name"].str.contains(
        "LLC|LP|CORP|INC|HDFC|ASSOCIATES", 
        case=False, 
        na=False
    )

    df["residential"] = df["residential"].apply(
        lambda x: "Yes" if str(x).upper() == "YES" else "No"
    )

    df = df[[
        "address", "zip_code", "job_type", "job_type_label",
        "permit_type", "permit_type_label", "permit_status",
        "filing_date", "owner", "is_llc",
        "gis_latitude", "gis_longitude", "gis_council_district",
        "community_board", "residential", "block", "lot"
    ]].drop_duplicates()

    df = df.sort_values("filing_date", ascending=False)
    df.to_csv("data/permits.csv", index=False)
    print(f"\nSaved {len(df)} permits to data/permits.csv")
    return df

fetch_all_permits()