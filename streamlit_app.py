import datetime as dt

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Voyage Turquie 2026", page_icon="🇹🇷", layout="wide")

# ---------------------------------------------------------------------------
# Itinerary data
#
# Reconstructed from the trip spreadsheet. The sheet's blank "Journée" cells
# (in between the flight/road-trip days) are filled in below with a plain
# "stay" or "transfer" description derived from when the overnight location
# (Nuit) changes. Dates are assumed to fall in 2026 (Aug 29 -> Sep 13), since
# September only has 30 days and the sheet lists a "31" before day "1".
# ---------------------------------------------------------------------------

LOCATION_COLORS = {
    "Antalya": "#2a78d6",
    "Göreme": "#008300",
    "Kas": "#eda100",
    "Fethiye": "#1baf7a",
    "Barcelone/Nivelles": "#eb6834",
}

LOCATION_COORDS = {
    "Antalya": (36.8969, 30.7133),
    "Göreme": (38.6431, 34.8286),
    "Kas": (36.2020, 29.6390),
    "Fethiye": (36.6217, 29.1164),
    "Barcelone/Nivelles": (41.3874, 2.1686),
}

# Points of interest to consider visiting/day-tripping to, not on the core itinerary.
POINTS_OF_INTEREST = {
    "Olympos": (36.4167, 30.4667),
    "Cirali": (36.4333, 30.4833),
    "Kastellorizo": (36.1499, 29.5883),
    "Plage de Kaputas": (36.1699, 29.6216),
    "Kekova island": (36.1904, 29.8724),
    "Demre": (36.2467, 29.9833),
    "Dalyan": (36.8386, 28.6478),
    "Egirdir": (37.8792, 30.8536),
    "Aspendos": (36.9351, 31.1725),
    "Koprulu Canyon National Park": (37.0122, 30.9350),
    "Cleopatra antique pools (Pamukkale)": (37.9236, 29.1211),
    "Goynuk Canyon": (36.5667, 30.5333),
    "Oludeniz": (36.5497, 29.1164),
    "Saklikent (canyon)": (36.5192, 29.3489),
    "Perge": (36.9611, 30.8514),
    "Termessos": (36.9814, 30.4547),
    "Patara": (36.2649, 29.3169),
    "Presqu'ile Datca": (36.7307, 27.6836),
    "Pamukkale": (37.9200, 29.1200),
    "Chutes Duden": (36.9214, 30.7908),
}

KAS_AIRBNB_ADDRESS = "Likya Caddesi No:14 / B, Kaş, Antalya 07580, Turkey"

ITINERARY = [
    dict(date=dt.date(2026, 8, 29), journee="Vol jusqu'à Antalya", nuit="Antalya", type="Vol ✈️"),
    dict(date=dt.date(2026, 8, 30), journee="Journée à Antalya", nuit="Antalya", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 8, 31), journee="Journée à Antalya", nuit="Antalya", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 1), journee="Route aller vers la Cappadoce", nuit="Göreme", type="Route 🚗"),
    dict(date=dt.date(2026, 9, 2), journee="Découverte de la Cappadoce", nuit="Göreme", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 3), journee="Découverte de la Cappadoce", nuit="Göreme", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 4), journee="Route retour de Cappadoce vers Kas", nuit="Kas", type="Route 🚗", adresse=KAS_AIRBNB_ADDRESS, trajet="~6h30 - 7h de route (≈500 km)"),
    dict(date=dt.date(2026, 9, 5), journee="Séjour à Kas", nuit="Kas", type="Séjour 🏖️", adresse=KAS_AIRBNB_ADDRESS),
    dict(date=dt.date(2026, 9, 6), journee="Séjour à Kas", nuit="Kas", type="Séjour 🏖️", adresse=KAS_AIRBNB_ADDRESS),
    dict(date=dt.date(2026, 9, 7), journee="Séjour à Kas", nuit="Kas", type="Séjour 🏖️", adresse=KAS_AIRBNB_ADDRESS),
    dict(date=dt.date(2026, 9, 8), journee="Transfert vers Fethiye", nuit="Fethiye", type="Route 🚗"),
    dict(date=dt.date(2026, 9, 9), journee="Séjour à Fethiye", nuit="Fethiye", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 10), journee="Séjour à Fethiye", nuit="Fethiye", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 11), journee="Séjour à Fethiye", nuit="Fethiye", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 12), journee="Transfert vers Antalya", nuit="Antalya", type="Route 🚗"),
    dict(date=dt.date(2026, 9, 13), journee="Vol retour depuis Antalya", nuit="Barcelone/Nivelles", type="Vol ✈️"),
]

df = pd.DataFrame(ITINERARY)
df["jour_num"] = range(1, len(df) + 1)
df["date_str"] = df["date"].apply(lambda d: d.strftime("%a %d %b"))

MONTH_NAMES_FR = {
    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
    7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre",
}
WEEKDAY_LABELS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]


def agenda_html(trip_df: pd.DataFrame) -> str:
    """Render only the trip's own days as a Google-Agenda-style list, grouped by month."""
    sections = ""
    for (year, month), month_df in trip_df.groupby(
        [trip_df["date"].apply(lambda d: d.year), trip_df["date"].apply(lambda d: d.month)], sort=False
    ):
        rows_html = ""
        for _, info in month_df.iterrows():
            d = info["date"]
            color = LOCATION_COLORS[info["nuit"]]
            dow = WEEKDAY_LABELS_FR[d.weekday()]
            adresse = info.get("adresse")
            trajet = info.get("trajet")
            adresse_html = f'<div class="agenda-adresse">🏠 {adresse}</div>' if pd.notna(adresse) else ""
            trajet_html = f'<div class="agenda-trajet">🚗 {trajet}</div>' if pd.notna(trajet) else ""
            rows_html += (
                '<div class="agenda-row">'
                '<div class="agenda-date">'
                f'<div class="agenda-daynum">{d.day}</div>'
                f'<div class="agenda-dow">{dow}</div>'
                "</div>"
                f'<div class="agenda-chip" style="border-left-color:{color};">'
                f'<span class="agenda-dot" style="background:{color};"></span>'
                '<div class="agenda-text">'
                f'<div class="agenda-loc">{info["nuit"]}</div>'
                f'<div class="agenda-desc">{info["journee"]}</div>'
                f"{trajet_html}"
                f"{adresse_html}"
                "</div>"
                "</div>"
                "</div>"
            )
        sections += f'<div class="agenda-month-title">{MONTH_NAMES_FR[month]} {year}</div>{rows_html}'
    return f'<div class="agenda-wrap">{sections}</div>'


CAL_CSS = """
<style>
.agenda-wrap { border: 1px solid rgba(11,11,11,0.10); border-radius: 8px; background: #fcfcfb; padding: 8px 12px; }
.agenda-month-title { font-weight: 600; font-size: 0.85rem; color: #898781; padding: 10px 4px 6px; text-transform: uppercase; letter-spacing: 0.02em; }
.agenda-row { display: flex; align-items: stretch; gap: 12px; padding: 6px 4px; border-bottom: 1px solid #e1e0d9; }
.agenda-row:last-child { border-bottom: none; }
.agenda-date { width: 44px; flex-shrink: 0; text-align: center; padding-top: 2px; }
.agenda-daynum { font-size: 1.05rem; font-weight: 700; color: #0b0b0b; line-height: 1.1; }
.agenda-dow { font-size: 0.68rem; color: #898781; text-transform: uppercase; }
.agenda-chip { flex: 1; display: flex; align-items: center; gap: 8px; border-left: 4px solid; border-radius: 4px; background: #f9f9f7; padding: 6px 10px; min-width: 0; }
.agenda-dot { display: none; }
.agenda-text { min-width: 0; }
.agenda-loc { font-size: 0.82rem; font-weight: 600; color: #0b0b0b; }
.agenda-desc { font-size: 0.74rem; color: #52514e; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.agenda-adresse { font-size: 0.7rem; color: #52514e; margin-top: 2px; }
.agenda-trajet { font-size: 0.7rem; color: #52514e; margin-top: 2px; }
</style>
"""

# ---------------------------------------------------------------------------
# Stay segments (consecutive nights in the same place) for the timeline chart
# ---------------------------------------------------------------------------

segments = []
current_loc = None
seg_start = None
prev_date = None
for _, row in df.iterrows():
    if row["nuit"] != current_loc:
        if current_loc is not None:
            segments.append(dict(location=current_loc, start=seg_start, end=row["date"], nights=(row["date"] - seg_start).days))
        current_loc = row["nuit"]
        seg_start = row["date"]
    prev_date = row["date"]
last_end = prev_date + dt.timedelta(days=1)
segments.append(dict(location=current_loc, start=seg_start, end=last_end, nights=(last_end - seg_start).days))
seg_df = pd.DataFrame(segments)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🇹🇷 Voyage en Turquie — 29 août au 13 septembre 2026")

trip_start = ITINERARY[0]["date"]
trip_end = ITINERARY[-1]["date"]
today = dt.date.today()
total_days = (trip_end - trip_start).days + 1
total_nights_turkey = sum(s["nights"] for s in segments if s["location"] != "Barcelone/Nivelles")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Durée totale", f"{total_days} jours")
col2.metric("Nuits en Turquie", total_nights_turkey)
col3.metric("Destinations", len(LOCATION_COLORS) - 1)
if today < trip_start:
    col4.metric("Départ dans", f"{(trip_start - today).days} jours")
elif today > trip_end:
    col4.metric("Statut", "Terminé")
else:
    day_idx = (today - trip_start).days + 1
    col4.metric("Jour actuel", f"{day_idx} / {total_days}")

st.divider()

tab_map, tab_timeline = st.tabs(["🗺️ Carte", "📅 Ligne du temps"])

# ---------------------------------------------------------------------------
# Timeline tab: gantt chart + stay summary
# ---------------------------------------------------------------------------

with tab_timeline:
    st.subheader("Calendrier du séjour")

    st.markdown(CAL_CSS, unsafe_allow_html=True)
    st.markdown(agenda_html(df), unsafe_allow_html=True)

    st.subheader("Récapitulatif par étape")
    summary_cols = st.columns(len(seg_df))
    for col, (_, seg) in zip(summary_cols, seg_df.iterrows()):
        with col:
            st.markdown(f"**{seg['location']}**")
            if seg["location"] == "Barcelone/Nivelles":
                st.caption(f"Arrivée le {seg['start'].strftime('%d %b')}")
            else:
                st.caption(f"{seg['start'].strftime('%d %b')} → {seg['end'].strftime('%d %b')}")
                st.caption(f"{seg['nights']} nuit(s)")

# ---------------------------------------------------------------------------
# Map tab
# ---------------------------------------------------------------------------

MAP_CATEGORY_COLORS = {
    "Étape du séjour": "#2a78d6",
    "Point d'intérêt": "#eb6834",
}

with tab_map:
    st.subheader("Turquie : étapes du séjour et idées d'excursions")

    stops_df = pd.DataFrame(
        [
            dict(location=loc, lat=coord[0], lon=coord[1], category="Étape du séjour")
            for loc, coord in LOCATION_COORDS.items()
            if loc != "Barcelone/Nivelles"
        ]
    )
    poi_df = pd.DataFrame(
        [
            dict(location=loc, lat=coord[0], lon=coord[1], category="Point d'intérêt")
            for loc, coord in POINTS_OF_INTEREST.items()
        ]
    )
    map_df = pd.concat([stops_df, poi_df], ignore_index=True)

    fig_map = px.scatter_geo(
        map_df,
        lat="lat",
        lon="lon",
        color="category",
        color_discrete_map=MAP_CATEGORY_COLORS,
        category_orders={"category": ["Étape du séjour", "Point d'intérêt"]},
        text="location",
        hover_name="location",
        fitbounds="locations",
    )
    fig_map.update_traces(marker=dict(size=10, line=dict(width=1, color="rgba(11,11,11,0.10)")), textposition="top center")
    fig_map.update_geos(
        showcountries=True,
        countrycolor="#e1e0d9",
        showland=True,
        landcolor="#fcfcfb",
        showocean=True,
        oceancolor="#eaf2fb",
        showlakes=False,
        resolution=50,
    )
    fig_map.update_layout(
        template="plotly_white",
        height=650,
        margin=dict(l=10, r=10, t=10, b=10),
        legend_title_text="Légende",
    )
    st.plotly_chart(fig_map, use_container_width=True)
