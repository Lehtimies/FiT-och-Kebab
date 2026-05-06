import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

BASE_URL = "https://sotkanet.fi/rest/1.1"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "rOpenGov/sotkanet"
}

def get_data(indicator_id, years, gender="total"):
    params = []
    for y in years:
        params.append(("years", y))
    params.append(("indicator", indicator_id))
    params.append(("genders", gender))

    response = requests.get(f"{BASE_URL}/json", headers=HEADERS, params=params)
    print("Status:", response.status_code)
    data = response.json()
    return pd.DataFrame(data)

def get_regions():
    response = requests.get(f"{BASE_URL}/regions", headers=HEADERS)
    return pd.DataFrame(response.json())

# Fetch indicator 4 (hospital care for mental disorders, ages 0-17)
df = get_data(indicator_id=4, years=range(2010, 2023))
print(df.head())
print("Columns:", df.columns.tolist())

# Load regions so we can look up names
regions = get_regions()
print(regions.head())
