

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
        print(f"  VARNING: indikator {indicator_id} returnerade HTTP {r.status_code}")
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
    print(f"  Sparad: {path}")


def line_chart(x, y, title, ylabel, color, filename):
    plt.figure(figsize=(9, 4))
    plt.plot(x, y, marker="o", color=color, linewidth=2)
    plt.title(title)
    plt.xlabel("År")
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


print("Laddar regioner...")
regions_raw = fetch_regions()
region_map = {r["id"]: r["title"].get("fi", "") for r in regions_raw}
NAT_ID = next(r["id"] for r in regions_raw if "koko maa" in r["title"].get("fi","").lower())
MAA_IDS = [r["id"] for r in regions_raw if r.get("category") == "MAAKUNTA"]

 


# Q1 Alkohol konsumption
print("\nQ1: Hur har alkoholkonsumtionen per capita förändrats på nationell nivå?")
df = fetch_data(1806, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q1: Alkoholkonsumtion per capita (liter ren alkohol), Finland",
               "Liter / invånare", "#2196F3", "q1_alcohol_consumption.png")

# Q2 Alkoholförsäljning per provins
print("\nQ2: Vilka provinser har högst alkoholförsäljning per capita?")
df = fetch_data(714, [2022, 2021])
if not df.empty:
    maa = province_latest(df, MAA_IDS, region_map)
    print(maa[["region_name", "value"]].to_string(index=False))
    bar_chart(maa["region_name"], maa["value"],
              "Q2: Alkoholförsäljning per capita per provins (liter ren alkohol)",
              "Liter / invånare", "#FF9800", "q2_alcohol_sales_province.png")

# Q3 Högsta alkoholkonsumtion
print("\nQ3: Vilket år hade högst alkoholkonsumtion på nationell nivå?")
df = fetch_data(1806, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    peak = nat.loc[nat["value"].idxmax()]
    print(f"  Toppår: {int(peak['year'])} med {peak['value']:.1f} liter per capita")


# =============================================================================
# TOPIC 2 – MENTAL HEALTH
# =============================================================================

# Q4 Psykiatriska öppenvårdsbesök
print("\nQ4: Hur har psykiatriska öppenvårdsbesök förändrats på nationell nivå?")
df = fetch_data(1272, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q4: Psykiatriska öppenvårdsbesök / 1 000 invånare, Finland",
               "Besök / 1 000", "#00BCD4", "q4_psychiatric_outpatient.png")

# Q5 Suicidmortalitet
print("\nQ5: Hur har suicidmortaliteten förändrats över tiden?")
df = fetch_data(179, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q5: Suicidmortalitet (åldersstandard / 100 000), Finland",
               "Dödsfall / 100 000", "#607D8B", "q5_suicide_mortality.png")

# Q6 Psykiatrisk sjukhusvård barn per kön
print("\nQ6: Får pojkar eller flickor mer psykiatrisk sjukhusvård (ålder 0-17)?")
df_m = fetch_data(4, YEARS, gender="male")
df_f = fetch_data(4, YEARS, gender="female")
if not df_m.empty and not df_f.empty:
    nat_m = national_series(df_m, NAT_ID)
    nat_f = national_series(df_f, NAT_ID)
    print("Man:"); print(nat_m[["year", "value"]].to_string(index=False))
    print("Kvinna:"); print(nat_f[["year", "value"]].to_string(index=False))
    plt.figure(figsize=(9, 4))
    plt.plot(nat_m["year"], nat_m["value"], marker="o", label="Man", color="#2196F3", linewidth=2)
    plt.plot(nat_f["year"], nat_f["value"], marker="o", label="Kvinna", color="#E91E63", linewidth=2)
    plt.title("Q6: Psykiatrisk sjukhusvård för 0-17 åringar / 1 000, per kön")
    plt.xlabel("År"); plt.ylabel("Per 1 000")
    plt.xticks(nat_m["year"], rotation=45)
    plt.ylim(bottom=0, top=max(nat_m["value"].max(), nat_f["value"].max()) * 1.2)
    plt.legend(); plt.grid(axis="y", alpha=0.4)
    savefig("q6_youth_mental_health_gender.png")

# Q7 Genomsnittlig suicidmortalitet
print("\nQ7: Vad var den genomsnittliga suicidmortaliteten mellan 2010 och 2023?")
df = fetch_data(179, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    avg = nat["value"].mean()
    print(f"  Genomsnittlig suicidmortalitet 2010-2023: {avg:.1f} per 100 000")


# =============================================================================
# TOPIC 3 – SOCIOECONOMIC FACTORS
# =============================================================================

# Q8 Socialbidrag
print("\nQ8: Hur har andelen socialbidragsmottagare (25-64) förändrats?")
df = fetch_data(5, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q8: Socialbidragsmottagare i åldern 25-64 (%), Finland",
               "% av åldersgruppen", "#FFC107", "q8_social_assistance.png")

# Q9 Socialbidrag per provins
print("\nQ9: Vilka provinser har högst socialbidragsfrekvenser?")
df = fetch_data(5, [2022, 2021])
if not df.empty:
    maa = province_latest(df, MAA_IDS, region_map)
    print(maa[["region_name", "value"]].to_string(index=False))
    bar_chart(maa["region_name"], maa["value"],
              "Q9: Socialbidragsmottagare 25-64 (%) per provins",
              "% av åldersgruppen", "#FFCA28", "q9_social_assistance_province.png")

# Q10 Skolavhoppningsfrekvens
print("\nQ10: Vad är den nuvarande skolavhoppningsfrekvensen bland 17-24 åringar?")
df = fetch_data(234, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    latest = nat.iloc[-1]
    print(f"  Senaste året {int(latest['year'])}: {latest['value']:.1f}% utan kvalifikation")


# =============================================================================
# TOPIC 4 – CHILDREN & YOUTH
# =============================================================================

# Q11 Skolavhoppningsfrekvens trend
print("\nQ11: Hur har skolavhoppningsfrekvensen bland 17-24 åringar förändrats över tiden?")
df = fetch_data(234, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q11: Skolavhoppare i åldern 17-24 (% utan kvalifikation), Finland",
               "% av åldersgruppen", "#3F51B5", "q11_school_dropouts.png")

# Q12 Ungdomars övervikt
print("\nQ12: Hur har övervikt/fetma bland 8:e-9:e klassare förändrats över tiden?")
df = fetch_data(3052, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))
    line_chart(nat["year"], nat["value"],
               "Q12: Överviktiga eller feta 8:e-9:e klassare (%), Finland",
               "% av eleverna", "#8BC34A", "q12_youth_overweight.png")


# =============================================================================
# SUMMARY
# =============================================================================
print(f"\nUtdata sparad i ./{OUTPUT_DIR}/")
for f in sorted(os.listdir(OUTPUT_DIR)):
    print(f"  {f}")