"""
=============================================================
Forskningsmetodik för IT - Projekt 3
Titel:  Hälsa och välfärd i Finland – en dataanalys
Källa:  THL Sotkanet API  https://sotkanet.fi
        CC BY 4.0 – Terveyden ja hyvinvoinnin laitos (THL)
=============================================================
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

BASE_URL = "https://sotkanet.fi/rest/1.1"
HEADERS = {"Accept": "application/json", "User-Agent": "rOpenGov/sotkanet"}
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
YEARS = list(range(2010, 2024))


def fetch_data(indicator_id, years, gender="total"):
    params = [("indicator", indicator_id), ("genders", gender)]
    for y in years:
        params.append(("years", y))
    r = requests.get(f"{BASE_URL}/json", headers=HEADERS, params=params)
    if r.status_code != 200:
        print(f"  WARNING: indicator {indicator_id} returned HTTP {r.status_code}")
        return pd.DataFrame()
    data = r.json()
    return pd.DataFrame(data) if data else pd.DataFrame()


def fetch_regions():
    r = requests.get(f"{BASE_URL}/regions", headers=HEADERS)
    return r.json()


def national_series(df, nat_id):
    return df[df["region"] == nat_id].sort_values("year")


def province_latest(df, maa_ids, rmap):
    d = df[df["region"].isin(maa_ids)].copy()
    d = d.sort_values("year", ascending=False).drop_duplicates("region")
    d["region_name"] = d["region"].map(rmap)
    return d.dropna(subset=["value"]).sort_values("value", ascending=False)


def savefig(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


def line_chart(x, y, title, ylabel, color, filename):
    plt.figure(figsize=(9, 4))
    plt.plot(x, y, marker="o", color=color, linewidth=2)
    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel(ylabel)
    plt.xticks(x, rotation=45)
    # Smart y-axis: zoom in if the data range is narrow relative to its magnitude
    ymin, ymax = min(y), max(y)
    padding = (ymax - ymin) * 0.3 or ymax * 0.1
    if ymin > ymax * 0.2:
        plt.ylim(bottom=max(0, ymin - padding * 2), top=ymax + padding)
    else:
        plt.ylim(bottom=0, top=ymax * 1.2)
    plt.grid(axis="y", alpha=0.4)
    savefig(filename)


def bar_chart(names, values, title, xlabel, color, filename):
    plt.figure(figsize=(10, 6))
    plt.barh(list(names), list(values), color=color)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.xlim(left=0, right=max(values) * 1.15)
    plt.gca().invert_yaxis()
    savefig(filename)


def section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ── Load regions ──────────────────────────────────────────────────────────────
print("Loading regions...")
regions_raw = fetch_regions()
region_map = {r["id"]: r["title"].get("fi", "") for r in regions_raw}
NAT_ID = next(r["id"] for r in regions_raw if "koko maa" in r["title"].get("fi","").lower())
MAA_IDS = [r["id"] for r in regions_raw if r.get("category") == "MAAKUNTA"]


# =============================================================================
# TOPIC 1 – SUBSTANCE USE
# =============================================================================
section("TOPIC 1 – SUBSTANCE USE")

# Q1 (visual): Alcohol consumption per capita trend
print("\nQ1: How has alcohol consumption per capita changed nationally?")
df = fetch_data(1806, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q1: Alcohol consumption per capita (litres pure alcohol), Finland",
               "Litres / inhabitant", "#2196F3", "q1_alcohol_consumption.png")

# Q2 (visual): Alcohol sales by province
print("\nQ2: Which provinces have the highest alcohol sales per capita?")
df = fetch_data(714, [2022, 2021])
if not df.empty:
    maa = province_latest(df, MAA_IDS, region_map)
    print(maa[["region_name", "value"]].to_string(index=False))
    bar_chart(maa["region_name"], maa["value"],
              "Q2: Alcohol sales per capita by province (litres pure alcohol)",
              "Litres / inhabitant", "#FF9800", "q2_alcohol_sales_province.png")

# Q3 (no visual): Which year had the highest alcohol consumption?
print("\nQ3: Which year had the highest alcohol consumption nationally?")
df = fetch_data(1806, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    peak = nat.loc[nat["value"].idxmax()]
    print(f"  Peak year: {int(peak['year'])} with {peak['value']:.1f} litres per capita")


# =============================================================================
# TOPIC 2 – MENTAL HEALTH
# =============================================================================
section("TOPIC 2 – MENTAL HEALTH")

# Q4 (visual): Psychiatric outpatient visits trend
print("\nQ4: How have psychiatric outpatient visits changed nationally?")
df = fetch_data(1272, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q4: Psychiatric outpatient visits / 1 000 inhabitants, Finland",
               "Visits / 1 000", "#00BCD4", "q4_psychiatric_outpatient.png")

# Q5 (visual): Suicide mortality trend
print("\nQ5: How has suicide mortality changed over time?")
df = fetch_data(179, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q5: Suicide mortality (age-standardised / 100 000), Finland",
               "Deaths / 100 000", "#607D8B", "q5_suicide_mortality.png")

# Q6 (visual): Psychiatric hospital care for children by gender
print("\nQ6: Do boys or girls receive more psychiatric hospital care (ages 0-17)?")
df_m = fetch_data(4, YEARS, gender="male")
df_f = fetch_data(4, YEARS, gender="female")
if not df_m.empty and not df_f.empty:
    nat_m = national_series(df_m, NAT_ID)
    nat_f = national_series(df_f, NAT_ID)
    print("Male:"); print(nat_m[["year", "value"]].to_string(index=False))
    print("Female:"); print(nat_f[["year", "value"]].to_string(index=False))
    plt.figure(figsize=(9, 4))
    plt.plot(nat_m["year"], nat_m["value"], marker="o", label="Male", color="#2196F3", linewidth=2)
    plt.plot(nat_f["year"], nat_f["value"], marker="o", label="Female", color="#E91E63", linewidth=2)
    plt.title("Q6: Psychiatric hospital care for 0-17 year olds / 1 000, by gender")
    plt.xlabel("Year"); plt.ylabel("Per 1 000")
    plt.xticks(nat_m["year"], rotation=45)
    plt.ylim(bottom=0, top=max(nat_m["value"].max(), nat_f["value"].max()) * 1.2)
    plt.legend(); plt.grid(axis="y", alpha=0.4)
    savefig("q6_youth_mental_health_gender.png")

# Q7 (no visual): Average suicide rate over the period
print("\nQ7: What was the average suicide mortality rate between 2010 and 2023?")
df = fetch_data(179, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    avg = nat["value"].mean()
    print(f"  Average suicide mortality 2010-2023: {avg:.1f} per 100 000")


# =============================================================================
# TOPIC 3 – SOCIOECONOMIC FACTORS
# =============================================================================
section("TOPIC 3 – SOCIOECONOMIC FACTORS")

# Q8 (visual): Social assistance trend
print("\nQ8: How has the share of social assistance recipients (25-64) changed?")
df = fetch_data(5, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q8: Social assistance recipients aged 25-64 (%), Finland",
               "% of age group", "#FFC107", "q8_social_assistance.png")

# Q9 (visual): Social assistance by province
print("\nQ9: Which provinces have the highest social assistance rates?")
df = fetch_data(5, [2022, 2021])
if not df.empty:
    maa = province_latest(df, MAA_IDS, region_map)
    print(maa[["region_name", "value"]].to_string(index=False))
    bar_chart(maa["region_name"], maa["value"],
              "Q9: Social assistance recipients 25-64 (%) by province",
              "% of age group", "#FFCA28", "q9_social_assistance_province.png")

# Q10 (no visual): School dropout rate latest value
print("\nQ10: What is the current school dropout rate among 17-24 year olds?")
df = fetch_data(234, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    latest = nat.iloc[-1]
    print(f"  Most recent year {int(latest['year'])}: {latest['value']:.1f}% without qualification")


# =============================================================================
# TOPIC 4 – CHILDREN & YOUTH
# =============================================================================
section("TOPIC 4 – CHILDREN & YOUTH")

# Q11 (visual): School dropouts trend
print("\nQ11: How has the school dropout rate among 17-24 year olds changed over time?")
df = fetch_data(234, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q11: School dropouts aged 17-24 (% without qualification), Finland",
               "% of age group", "#3F51B5", "q11_school_dropouts.png")

# Q12 (visual): Youth overweight trend
print("\nQ12: How has overweight/obesity among 8th-9th graders changed over time?")
df = fetch_data(3052, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q12: Overweight or obese 8th-9th graders (%), Finland",
               "% of students", "#8BC34A", "q12_youth_overweight.png")


# =============================================================================
# SUMMARY
# =============================================================================
section("ALL DONE")
print(f"\nOutput saved to ./{OUTPUT_DIR}/")
for f in sorted(os.listdir(OUTPUT_DIR)):
    print(f"  {f}")