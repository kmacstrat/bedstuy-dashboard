import requests
import pandas as pd

DATASET_ID = "rbx6-tga4"
BASE_URL = f"https://data.cityofnewyork.us/resource/{DATASET_ID}.json"

BEDSTUY_NTАС = [
    "Bedford-Stuyvesant (West)",
    "Bedford-Stuyvesant (East)",
    "Bedford-Stuyvesant"
]

BEDSTUY_ZIPS = ["11205", "11206", "11216", "11221", "11233"]

JOB_TYPE_LABELS = {
    "New Building": "New Building",
    "Alteration": "Alteration",
    "Demolition": "Demolition",
    "Foundation": "Foundation",
    "Plumbing": "Plumbing",
    "Mechanical": "Mechanical",
    "Sidewalk Shed": "Sidewalk Shed",
    "Scaffold": "Scaffold",
}

def fetch_permits(limit=2000):
    all_permits = []

    # fetch by zip code
    for zip_code in BEDSTUY_ZIPS:
        print(f"Fetching permits for zip {zip_code}...")
        url = (
            f"{BASE_URL}?zip_code={zip_code}"
            f"&$limit={limit}"
            f"&$order=issued_date DESC"
        )
        response = requests.get(url)
        data = response.json()
        all_permits.extend(data)
        print(f"  Got {len(data)} permits")

    df = pd.DataFrame(all_permits)
    print(f"\nTotal before dedup: {len(df)}")

    # clean dates
    df["filing_date"] = pd.to_datetime(df["issued_date"], errors="coerce")
    df = df.dropna(subset=["filing_date"])

    # clean owner
    df["owner"] = df.apply(
        lambda r: r.get("owner_business_name", "")
        if r.get("owner_business_name") not in ["N/A", "", None]
        else r.get("owner_name", "Unknown"),
        axis=1
    )

    # full address
    df["address"] = (
        df["house_no"].astype(str) + " " +
        df["street_name"].astype(str) +
        ", Brooklyn NY " +
        df["zip_code"].astype(str)
    )

    # LLC flag
    df["is_llc"] = df["owner"].str.contains(
        "LLC|LP|CORP|INC|HDFC|ASSOCIATES|AUTHORITY",
        case=False,
        na=False
    )

    # residential flag -- DOB NOW uses job_description
    df["residential"] = df["job_description"].str.contains(
        "residential|dwelling|apartment|housing|hdfc",
        case=False,
        na=False
    ).map({True: "Yes", False: "No"})

    # job type label -- use work_type directly
    df["job_type"] = df["work_type"].fillna("Unknown")
    df["job_type_label"] = df["job_type"]

    # permit status
    df["permit_status"] = df["permit_status"].fillna("Unknown")

    # council district and community board
    df["gis_council_district"] = df["council_district"]
    df["community_board"] = df["c_b_no"]

    # coordinates
    df["gis_latitude"] = df["latitude"]
    df["gis_longitude"] = df["longitude"]

    # estimated cost -- useful for story
    df["estimated_cost"] = pd.to_numeric(
        df["estimated_job_costs"], errors="coerce"
    )

    # neighborhood
    df["neighborhood"] = df.get("nta", "Bedford-Stuyvesant")

    # keep useful columns
    df = df[[
        "address", "zip_code", "job_type", "job_type_label",
        "permit_status", "filing_date", "owner", "is_llc",
        "gis_latitude", "gis_longitude", "gis_council_district",
        "community_board", "residential", "block", "lot",
        "job_description", "estimated_cost", "neighborhood"
    ]].drop_duplicates()

    df = df.sort_values("filing_date", ascending=False)
    df.to_csv("data/permits.csv", index=False)
    print(f"Saved {len(df)} permits to data/permits.csv")
    return df

fetch_permits()