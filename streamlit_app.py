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

ITINERARY = [
    dict(date=dt.date(2026, 8, 29), journee="Vol jusqu'à Antalya", nuit="Antalya", type="Vol ✈️"),
    dict(date=dt.date(2026, 8, 30), journee="Journée à Antalya", nuit="Antalya", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 8, 31), journee="Journée à Antalya", nuit="Antalya", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 1), journee="Route aller vers la Cappadoce", nuit="Göreme", type="Route 🚗"),
    dict(date=dt.date(2026, 9, 2), journee="Découverte de la Cappadoce", nuit="Göreme", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 3), journee="Découverte de la Cappadoce", nuit="Göreme", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 4), journee="Route retour de Cappadoce vers Kas", nuit="Kas", type="Route 🚗"),
    dict(date=dt.date(2026, 9, 5), journee="Séjour à Kas", nuit="Kas", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 6), journee="Séjour à Kas", nuit="Kas", type="Séjour 🏖️"),
    dict(date=dt.date(2026, 9, 7), journee="Séjour à Kas", nuit="Kas", type="Séjour 🏖️"),
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
    st.subheader("Frise chronologique du séjour")

    fig = px.timeline(
        seg_df,
        x_start="start",
        x_end="end",
        y=[""] * len(seg_df),
        color="location",
        color_discrete_map=LOCATION_COLORS,
        category_orders={"location": list(LOCATION_COLORS.keys())},
        hover_data={"nights": True, "start": True, "end": True},
    )
    fig.update_yaxes(visible=False)
    fig.update_traces(marker_line_width=1, marker_line_color="rgba(11,11,11,0.10)")
    fig.update_layout(
        template="plotly_white",
        height=220,
        legend_title_text="Étape",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)

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
