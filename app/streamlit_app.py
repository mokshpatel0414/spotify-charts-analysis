"""
Spotify Charts Cross-Market Analysis Dashboard
Run locally with: streamlit run app/streamlit_app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Page setup
st.set_page_config(
    page_title="Spotify Charts Analysis",
    page_icon="🎵",
    layout="wide",
)

# Load data (cached so it only happens once per session)
DATA_DIR = Path(__file__).parent.parent / "data"

@st.cache_data
def load_data():
    q1 = pd.read_csv(DATA_DIR / "01_market_concentration.csv")
    q2 = pd.read_csv(DATA_DIR / "02_song_lifecycle_by_era.csv")
    q3 = pd.read_csv(DATA_DIR / "03_artist_dominance.csv")
    return q1, q2, q3

q1, q2, q3 = load_data()


# Header
st.title("Spotify Charts: A Cross-Market Analysis")
st.markdown(
    "How music consumption differs across 54 countries, "
    "based on 26 million Spotify chart entries from 2017 to 2021."
)

st.divider()


# Sidebar: country selector
st.sidebar.header("Explore by country")
countries = sorted(q1[q1["region"] != "Global"]["region"].tolist())
selected_country = st.sidebar.selectbox("Pick a country", countries, index=countries.index("United States"))


# Show the selected country's stats
country_q1 = q1[q1["region"] == selected_country].iloc[0]
country_q3 = q3[q3["region"] == selected_country].iloc[0]

st.subheader(f"{selected_country} at a glance")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Top-charting artist",
    country_q3["top_artist"],
)
col2.metric(
    "Their chart share",
    f"{country_q3['top_artist_share_pct']:.2f}%",
)
col3.metric(
    "Top 10 share of chart",
    f"{country_q1['pct_from_top10']:.1f}%",
)

# Concentration ranking
concentration_rank = (q1[q1["region"] != "Global"]
                      .sort_values("pct_from_top10", ascending=False)
                      .reset_index(drop=True))
rank = concentration_rank[concentration_rank["region"] == selected_country].index[0] + 1
total = len(concentration_rank)
st.caption(f"{selected_country} ranks **#{rank} out of {total}** in chart concentration.")

st.divider()


# Tabs: the three findings
tab1, tab2, tab3 = st.tabs([
    "Market concentration",
    "Song lifecycle",
    "Artist dominance (world map)"
])


# Tab 1: Market concentration
with tab1:
    st.subheader("Asia listens to fewer artists, Europe listens to more")
    st.markdown(
        "% of chart slots held by the top 10 artists, by country (2017 to 2021)."
    )
    
    # Same chart logic as in the notebook
    region_map = {
        "Netherlands": "Western Europe", "Austria": "Western Europe",
        "Germany": "Western Europe", "Switzerland": "Western Europe",
        "Belgium": "Western Europe", "France": "Western Europe",
        "Italy": "Western Europe", "Portugal": "Western Europe",
        "Ireland": "Western Europe", "United Kingdom": "Western Europe",
        "Spain": "Western Europe",
        "Sweden": "Nordic", "Norway": "Nordic", "Finland": "Nordic",
        "Denmark": "Nordic", "Iceland": "Nordic",
        "Poland": "Eastern Europe", "Czech Republic": "Eastern Europe",
        "Hungary": "Eastern Europe", "Slovakia": "Eastern Europe",
        "Lithuania": "Eastern Europe", "Latvia": "Eastern Europe",
        "Estonia": "Eastern Europe", "Greece": "Eastern Europe",
        "Turkey": "Eastern Europe",
        "Brazil": "Latin America", "Mexico": "Latin America",
        "Argentina": "Latin America", "Colombia": "Latin America",
        "Chile": "Latin America", "Peru": "Latin America",
        "Ecuador": "Latin America", "Uruguay": "Latin America",
        "Paraguay": "Latin America", "Bolivia": "Latin America",
        "Costa Rica": "Latin America", "Panama": "Latin America",
        "Guatemala": "Latin America", "Honduras": "Latin America",
        "El Salvador": "Latin America", "Dominican Republic": "Latin America",
        "Japan": "Asia", "Singapore": "Asia", "Hong Kong": "Asia",
        "Taiwan": "Asia", "Indonesia": "Asia", "Malaysia": "Asia",
        "Philippines": "Asia", "Thailand": "Asia",
        "United States": "North America", "Canada": "North America",
        "Australia": "Oceania", "New Zealand": "Oceania",
        "Global": "Global",
    }
    
    q1_chart = q1.copy()
    q1_chart["region_group"] = q1_chart["region"].map(region_map)
    region_order = ["Asia", "North America", "Oceania", "Eastern Europe",
                    "Nordic", "Latin America", "Western Europe", "Global"]
    q1_chart["region_group"] = pd.Categorical(q1_chart["region_group"], categories=region_order, ordered=True)
    q1_chart = q1_chart.sort_values(["region_group", "pct_from_top10"], ascending=[True, False])
    
    region_colors = {
        "Asia": "#d62728", "North America": "#ff7f0e", "Oceania": "#bcbd22",
        "Eastern Europe": "#9467bd", "Nordic": "#17becf",
        "Latin America": "#2ca02c", "Western Europe": "#1f77b4",
        "Global": "#7f7f7f",
    }
    
    fig1 = px.bar(
        q1_chart, x="pct_from_top10", y="region", color="region_group",
        color_discrete_map=region_colors, orientation="h",
        labels={"pct_from_top10": "Share from top 10 artists (%)", "region": "", "region_group": "Region"},
        height=1000,
        category_orders={"region": q1_chart["region"].tolist()},
    )
    fig1.update_traces(
        texttemplate="%{x:.1f}%",
        textposition="outside",
        textfont=dict(size=10, color="black"),
    )
    fig1.update_layout(plot_bgcolor="white", margin=dict(l=10, r=100, t=20, b=40))
    
    st.plotly_chart(fig1, use_container_width=True)


with tab2:
    st.subheader("Songs reach #1 faster and burn out quicker")
    st.markdown(
        "Among US chart-toppers from 2017 to 2021, the time it took to reach #1 fell from "
        "22.6 days to 5.7 days, and total chart lifespan halved (452 days to 199)."
    )
    
    q2_long = q2.melt(
        id_vars="era",
        value_vars=["avg_days_to_climb", "avg_days_at_top", "avg_total_days_on_chart"],
        var_name="metric", value_name="days"
    )
    metric_labels = {
        "avg_days_to_climb": "Days to reach #1",
        "avg_days_at_top": "Days at #1",
        "avg_total_days_on_chart": "Total days on chart",
    }
    q2_long["metric"] = q2_long["metric"].map(metric_labels)
    
    # Lock the order of metrics on the x-axis
    metric_order = ["Days to reach #1", "Days at #1", "Total days on chart"]
    q2_long["metric"] = pd.Categorical(q2_long["metric"], categories=metric_order, ordered=True)
    
    era_order = ["Early (2017-18)", "Mid (2019-mid 2020)", "Late (mid 2020-21)"]
    q2_long["era"] = pd.Categorical(q2_long["era"], categories=era_order, ordered=True)
    q2_long = q2_long.sort_values(["metric", "era"])
    
    era_colors = {
        "Early (2017-18)": "#a8c5e8",
        "Mid (2019-mid 2020)": "#5c8ec9",
        "Late (mid 2020-21)": "#1f4e79",
    }
    
    fig2 = px.bar(
        q2_long, x="metric", y="days", color="era",
        color_discrete_map=era_colors, barmode="group",
        labels={"metric": "", "days": "Days (average)", "era": "Era"},
        height=500, text="days",
        category_orders={
            "metric": metric_order,
            "era": era_order,
        },
    )
    fig2.update_traces(
        texttemplate="%{text:.0f}",
        textposition="outside",
        textfont=dict(size=12, color="black"),
    )
    fig2.update_layout(plot_bgcolor="white", bargap=0.25, bargroupgap=0.1)
    
    st.plotly_chart(fig2, use_container_width=True)

# Tab 3: World map
with tab3:
    st.subheader("Two artists own most of the world")
    st.markdown(
        "Most-charting artist per country across the 2017 to 2021 Spotify top 200. "
        "Bad Bunny dominates 13 countries (Latin America plus Spain), "
        "Ed Sheeran dominates 15 (English-speaking world plus Northern Europe), "
        "Drake's dominance is limited to Canada."
    )
    
    country_iso = {
        "United States": "USA", "Canada": "CAN", "Mexico": "MEX",
        "Brazil": "BRA", "Argentina": "ARG", "Colombia": "COL",
        "Chile": "CHL", "Peru": "PER", "Ecuador": "ECU",
        "Uruguay": "URY", "Paraguay": "PRY", "Bolivia": "BOL",
        "Costa Rica": "CRI", "Panama": "PAN", "Guatemala": "GTM",
        "Honduras": "HND", "El Salvador": "SLV", "Dominican Republic": "DOM",
        "United Kingdom": "GBR", "Ireland": "IRL", "France": "FRA",
        "Spain": "ESP", "Portugal": "PRT", "Italy": "ITA",
        "Germany": "DEU", "Austria": "AUT", "Switzerland": "CHE",
        "Belgium": "BEL", "Netherlands": "NLD",
        "Sweden": "SWE", "Norway": "NOR", "Denmark": "DNK",
        "Finland": "FIN", "Iceland": "ISL",
        "Poland": "POL", "Czech Republic": "CZE", "Hungary": "HUN",
        "Slovakia": "SVK", "Lithuania": "LTU", "Latvia": "LVA",
        "Estonia": "EST", "Greece": "GRC", "Turkey": "TUR",
        "Japan": "JPN", "Singapore": "SGP", "Hong Kong": "HKG",
        "Taiwan": "TWN", "Indonesia": "IDN", "Malaysia": "MYS",
        "Philippines": "PHL", "Thailand": "THA",
        "Australia": "AUS", "New Zealand": "NZL",
    }
    
    q3_map = q3[q3["region"] != "Global"].copy()
    q3_map["iso_code"] = q3_map["region"].map(country_iso)
    
    hero_artists = ["Bad Bunny", "Ed Sheeran", "Drake"]
    q3_map["artist_group"] = q3_map["top_artist"].apply(
        lambda x: x if x in hero_artists else "Other regional artist"
    )
    artist_order = ["Bad Bunny", "Ed Sheeran", "Drake", "Other regional artist"]
    q3_map["artist_group"] = pd.Categorical(q3_map["artist_group"], categories=artist_order, ordered=True)
    
    artist_colors = {
        "Bad Bunny": "#e74c3c", "Ed Sheeran": "#3498db",
        "Drake": "#9b59b6", "Other regional artist": "#bdc3c7",
    }
    
    fig3 = px.choropleth(
        q3_map,
        locations="iso_code",
        color="artist_group",
        hover_name="region",
        hover_data={
            "top_artist": True,
            "top_artist_share_pct": ":.2f",
            "iso_code": False,
            "artist_group": False,
        },
        color_discrete_map=artist_colors,
        labels={"artist_group": "Top-charting artist"},
    )
    
    fig3.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            showframe=False,
            projection_type="natural earth",
            bgcolor="white",
            showcountries=True,
            countrycolor="#aaa",
            countrywidth=0.5,
        ),
        height=600,
    )
    
    st.plotly_chart(fig3, use_container_width=True)


# Footer
st.divider()
st.caption(
    "Built with SQL (DuckDB), Python (pandas, plotly), and Streamlit. "
    "Source data: [Spotify Charts on Kaggle](https://www.kaggle.com/datasets/dhruvildave/spotify-charts). "
    "Repo: [github.com/mokshpatel0414/spotify-charts-analysis](https://github.com/mokshpatel0414/spotify-charts-analysis)."
)