"""
=============================================================
Forskningsmetodik för IT - Projekt 3
Titel:  Hälsa och välfärd i Finland – en dataanalys
Ämnen:  Mental hälsa, substansbruk, äldrevård, fetma,
        socioekonomiska faktorer, barn och unga
Källa:  THL Sotkanet API  https://sotkanet.fi
        CC BY 4.0 – Terveyden ja hyvinvoinnin laitos (THL)
=============================================================

Indikatorer som används:
  1806 - Alkoholijuomien kulutus, litraa 100% alkoholia / asukas
  176  - Alkoholisyihin kuolleet, ikävakioitu kuolleisuus / 100 000
  164  - Alkoholisairauksien vuodeosastohoitojaksot / 1 000 asukasta
  1982 - Huumausainerikokset / 1 000 asukasta
  1272 - Psykiatrian avohoitokäynnit / 1 000 asukasta
  3050 - Masentuneisuus, % (kouluterveyskysely 8-9 lk)
  179  - Itsemurhat, ikävakioitu kuolleisuus / 100 000
  4    - Mielenterveyden häiriöihin sairaalahoitoa saaneet 0-17v / 1 000
  3    - Somaattisen erikoissairaanhoidon hoitopäivät 75v+ / 1 000
  3136 - Yksinäisyyttä kokevat 75 vuotta täyttäneet, %
  2433 - Lihavuus (BMI >= 30), % aikuisväestöstä
  3052 - Ylipaino tai lihavuus, % (kouluterveyskysely 8-9 lk)
  5    - Toimeentulotukea saaneet 25-64v, % väestöstä
  180  - Pitkäaikaistyöttömät, % työvoimasta
  234  - Koulupudokkaat, % 17-24v (ei tutkintoa, ei opiskelija)
"""

import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

# ── Configuration ─────────────────────────────────────────────────────────────
BASE_URL = "https://sotkanet.fi/rest/1.1"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "rOpenGov/sotkanet"
}
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

YEARS = list(range(2010, 2024))


# ── Helper functions ──────────────────────────────────────────────────────────

def fetch_data(indicator_id, years, gender="total"):
    """
    Fetch indicator data from Sotkanet REST API.
    Returns a pandas DataFrame with columns:
      indicator, region, year, gender, value
    """
    params = [("indicator", indicator_id), ("genders", gender)]
    for y in years:
        params.append(("years", y))
    r = requests.get(f"{BASE_URL}/json", headers=HEADERS, params=params)
    if r.status_code != 200:
        print(f"  WARNING: indicator {indicator_id} returned HTTP {r.status_code}")
        return pd.DataFrame()
    data = r.json()
    if not data:
        print(f"  WARNING: indicator {indicator_id} returned empty data")
        return pd.DataFrame()
    return pd.DataFrame(data)


def fetch_regions():
    """Fetch all region metadata from Sotkanet."""
    r = requests.get(f"{BASE_URL}/regions", headers=HEADERS)
    return r.json()


def national_id(regions_raw):
    """Return the region id for 'Koko maa' (whole country)."""
    for reg in regions_raw:
        if "koko maa" in reg["title"].get("fi", "").lower():
            return reg["id"]
    return None


def maakunta_ids(regions_raw):
    """Return list of region ids at MAAKUNTA (province) level."""
    return [r["id"] for r in regions_raw if r.get("category") == "MAAKUNTA"]


def savefig(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


def section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def national_series(df, nat_id):
    """Filter to national region and sort by year."""
    return df[df["region"] == nat_id].sort_values("year")


def province_latest(df, maa_ids, rmap, years_pref):
    """
    For a list of preferred years, return per-province data for the
    most recent available year.
    """
    df_maa = df[df["region"].isin(maa_ids)].copy()
    df_maa = df_maa.sort_values("year", ascending=False).drop_duplicates("region")
    df_maa["region_name"] = df_maa["region"].map(rmap)
    return df_maa.dropna(subset=["value"]).sort_values("value", ascending=False)


# ── Load region metadata ───────────────────────────────────────────────────────
print("Loading region metadata from Sotkanet...")
regions_raw = fetch_regions()
region_map = {r["id"]: r["title"].get("fi", "") for r in regions_raw}
NAT_ID = national_id(regions_raw)
MAA_IDS = maakunta_ids(regions_raw)
print(f"  National region id : {NAT_ID}")
print(f"  Province count     : {len(MAA_IDS)}")


# =============================================================================
# TOPIC 1: SUBSTANCE USE
# =============================================================================
section("TOPIC 1 – SUBSTANCE USE")

# ── Q1 ────────────────────────────────────────────────────────────────────────
print("\nQ1: How has alcohol consumption per capita changed nationally (2010-2023)?")
df = fetch_data(1806, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#2196F3", linewidth=2)
    plt.title("Q1: Alcohol consumption per capita (litres of pure alcohol), Finland")
    plt.xlabel("Year")
    plt.ylabel("Litres / inhabitant")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q1_alcohol_consumption.png")

# ── Q2 ────────────────────────────────────────────────────────────────────────
print("\nQ2: How has alcohol-related mortality changed over time nationally?")
df = fetch_data(176, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#F44336", linewidth=2)
    plt.title("Q2: Alcohol-related mortality (age-standardised / 100 000), Finland")
    plt.xlabel("Year")
    plt.ylabel("Deaths / 100 000")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q2_alcohol_mortality.png")

# ── Q3 ────────────────────────────────────────────────────────────────────────
print("\nQ3: Which provinces have the highest alcohol-related hospitalisation rates?")
df = fetch_data(164, [2022, 2021, 2020])
if not df.empty:
    maa = province_latest(df, MAA_IDS, region_map, [2022, 2021, 2020])
    print(maa[["region_name", "value"]].to_string(index=False))

    plt.figure(figsize=(10, 6))
    plt.barh(maa["region_name"], maa["value"], color="#FF9800")
    plt.title("Q3: Alcohol-related hospital admissions / 1 000 inhabitants by province")
    plt.xlabel("Admissions / 1 000")
    plt.gca().invert_yaxis()
    savefig("q3_alcohol_hospitalisations_province.png")

# ── Q4 ────────────────────────────────────────────────────────────────────────
print("\nQ4: How have drug-related offences changed nationally over time?")
df = fetch_data(1982, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#9C27B0", linewidth=2)
    plt.title("Q4: Drug-related offences / 1 000 inhabitants, Finland")
    plt.xlabel("Year")
    plt.ylabel("Offences / 1 000")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q4_drug_offences.png")


# =============================================================================
# TOPIC 2: MENTAL HEALTH
# =============================================================================
section("TOPIC 2 – MENTAL HEALTH")

# ── Q5 ────────────────────────────────────────────────────────────────────────
print("\nQ5: How have psychiatric outpatient visits changed nationally?")
df = fetch_data(1272, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#00BCD4", linewidth=2)
    plt.title("Q5: Psychiatric outpatient visits / 1 000 inhabitants, Finland")
    plt.xlabel("Year")
    plt.ylabel("Visits / 1 000")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q5_psychiatric_outpatient.png")

# ── Q6 ────────────────────────────────────────────────────────────────────────
print("\nQ6: What share of 8th-9th graders report feeling depressed, and how has it changed?")
df = fetch_data(3050, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#E91E63", linewidth=2)
    plt.title("Q6: Depression among 8th-9th graders (%), Finland")
    plt.xlabel("Year")
    plt.ylabel("% of students")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q6_youth_depression.png")

# ── Q7 ────────────────────────────────────────────────────────────────────────
print("\nQ7: How has suicide mortality changed over time?")
df = fetch_data(179, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#607D8B", linewidth=2)
    plt.title("Q7: Suicide mortality (age-standardised / 100 000), Finland")
    plt.xlabel("Year")
    plt.ylabel("Deaths / 100 000")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q7_suicide_mortality.png")

# ── Q8: Psychiatric hospital care for children, by gender ────────────────────
print("\nQ8: Do boys or girls receive more psychiatric hospital care (ages 0-17)?")
df_m = fetch_data(4, YEARS, gender="male")
df_f = fetch_data(4, YEARS, gender="female")
if not df_m.empty and not df_f.empty:
    nat_m = national_series(df_m, NAT_ID)
    nat_f = national_series(df_f, NAT_ID)
    print("Male:")
    print(nat_m[["year", "value"]].to_string(index=False))
    print("Female:")
    print(nat_f[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat_m["year"], nat_m["value"], marker="o", label="Male", color="#2196F3", linewidth=2)
    plt.plot(nat_f["year"], nat_f["value"], marker="o", label="Female", color="#E91E63", linewidth=2)
    plt.title("Q8: Psychiatric hospital care for 0-17 year olds / 1 000, by gender")
    plt.xlabel("Year")
    plt.ylabel("Per 1 000")
    plt.xticks(nat_m["year"], rotation=45)
    plt.legend()
    plt.grid(axis="y", alpha=0.4)
    savefig("q8_youth_mental_health_gender.png")


# =============================================================================
# TOPIC 3: ELDERLY CARE
# =============================================================================
section("TOPIC 3 – ELDERLY CARE")

# ── Q9 ────────────────────────────────────────────────────────────────────────
print("\nQ9: How have somatic specialist care days for 75+ changed nationally?")
df = fetch_data(3, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#FF5722", linewidth=2)
    plt.title("Q9: Somatic specialist care days for 75+ / 1 000, Finland")
    plt.xlabel("Year")
    plt.ylabel("Days / 1 000")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q9_elderly_hospital_days.png")

# ── Q10 ───────────────────────────────────────────────────────────────────────
print("\nQ10: Which provinces have the highest loneliness rates among 75+ year olds?")
df = fetch_data(3136, [2022, 2021, 2020, 2019])
if not df.empty:
    maa = province_latest(df, MAA_IDS, region_map, [2022, 2021, 2020, 2019])
    print(maa[["region_name", "value"]].to_string(index=False))

    plt.figure(figsize=(10, 6))
    plt.barh(maa["region_name"], maa["value"], color="#795548")
    plt.title("Q10: Loneliness among 75+ year olds (%) by province")
    plt.xlabel("% reporting loneliness")
    plt.gca().invert_yaxis()
    savefig("q10_elderly_loneliness_province.png")


# =============================================================================
# TOPIC 4: OBESITY & PHYSICAL INACTIVITY
# =============================================================================
section("TOPIC 4 – OBESITY & PHYSICAL INACTIVITY")

# ── Q11 ───────────────────────────────────────────────────────────────────────
print("\nQ11: How has adult obesity (BMI >= 30) changed nationally over time?")
df = fetch_data(2433, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#4CAF50", linewidth=2)
    plt.title("Q11: Adult obesity (BMI >= 30), % of adult population, Finland")
    plt.xlabel("Year")
    plt.ylabel("% of adults")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q11_adult_obesity.png")

# ── Q12 ───────────────────────────────────────────────────────────────────────
print("\nQ12: How has overweight/obesity among 8th-9th graders changed over time?")
df = fetch_data(3052, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#8BC34A", linewidth=2)
    plt.title("Q12: Overweight or obese 8th-9th graders (%), Finland")
    plt.xlabel("Year")
    plt.ylabel("% of students")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q12_youth_overweight.png")


# =============================================================================
# TOPIC 5: SOCIOECONOMIC FACTORS
# =============================================================================
section("TOPIC 5 – SOCIOECONOMIC FACTORS")

# ── Q13 ───────────────────────────────────────────────────────────────────────
print("\nQ13: How has the share of social assistance recipients (25-64) changed nationally?")
df = fetch_data(5, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#FFC107", linewidth=2)
    plt.title("Q13: Social assistance recipients aged 25-64 (%), Finland")
    plt.xlabel("Year")
    plt.ylabel("% of age group")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q13_social_assistance.png")

# ── Q14 ───────────────────────────────────────────────────────────────────────
print("\nQ14: Which provinces have the highest social assistance rates?")
df = fetch_data(5, [2022, 2021])
if not df.empty:
    maa = province_latest(df, MAA_IDS, region_map, [2022, 2021])
    print(maa[["region_name", "value"]].to_string(index=False))

    plt.figure(figsize=(10, 6))
    plt.barh(maa["region_name"], maa["value"], color="#FFCA28")
    plt.title("Q14: Social assistance recipients 25-64 (%) by province")
    plt.xlabel("% of age group")
    plt.gca().invert_yaxis()
    savefig("q14_social_assistance_province.png")

# ── Q15 ───────────────────────────────────────────────────────────────────────
print("\nQ15: How has long-term unemployment changed over time nationally?")
df = fetch_data(180, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#FF6F00", linewidth=2)
    plt.title("Q15: Long-term unemployed (% of labour force), Finland")
    plt.xlabel("Year")
    plt.ylabel("% of labour force")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q15_longterm_unemployment.png")


# =============================================================================
# TOPIC 6: CHILDREN & YOUTH
# =============================================================================
section("TOPIC 6 – CHILDREN & YOUTH")

# ── Q16 ───────────────────────────────────────────────────────────────────────
print("\nQ16: How has the school dropout rate among 17-24 year olds changed?")
df = fetch_data(234, YEARS)
if not df.empty:
    nat = national_series(df, NAT_ID)
    print(nat[["year", "value"]].to_string(index=False))

    plt.figure(figsize=(9, 4))
    plt.plot(nat["year"], nat["value"], marker="o", color="#3F51B5", linewidth=2)
    plt.title("Q16: School dropouts aged 17-24 (% without qualification), Finland")
    plt.xlabel("Year")
    plt.ylabel("% of age group")
    plt.xticks(nat["year"], rotation=45)
    plt.grid(axis="y", alpha=0.4)
    savefig("q16_school_dropouts.png")


# =============================================================================
# COMBINED CHART: Youth mental health vs social assistance trend
# (example of comparing two indicators in one chart)
# =============================================================================
section("BONUS: Combined chart – youth depression vs social assistance")

print("\nBonus: Comparing youth depression rate with social assistance rate over time")
df_dep = fetch_data(3050, YEARS)
df_soc = fetch_data(5, YEARS)

if not df_dep.empty and not df_soc.empty:
    nat_dep = national_series(df_dep, NAT_ID)
    nat_soc = national_series(df_soc, NAT_ID)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    ax1.plot(nat_dep["year"], nat_dep["value"], marker="o",
             color="#E91E63", label="Youth depression (%)", linewidth=2)
    ax2.plot(nat_soc["year"], nat_soc["value"], marker="s",
             color="#FFC107", label="Social assistance 25-64 (%)", linewidth=2, linestyle="--")

    ax1.set_xlabel("Year")
    ax1.set_ylabel("Youth depression (%)", color="#E91E63")
    ax2.set_ylabel("Social assistance (%)", color="#FFC107")
    ax1.set_xticks(nat_dep["year"])
    ax1.set_xticklabels(nat_dep["year"], rotation=45)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title("Youth depression rate vs social assistance rate, Finland")
    plt.tight_layout()
    savefig("bonus_depression_vs_social_assistance.png")


# =============================================================================
# FINAL SUMMARY
# =============================================================================
section("ALL DONE")
print(f"\nOutput files saved to ./{OUTPUT_DIR}/")
for f in sorted(os.listdir(OUTPUT_DIR)):
    print(f"  {f}")