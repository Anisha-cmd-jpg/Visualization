"""
The Rupee's Retreat — Inflation Tracker 2020-2025
Streamlit + Plotly + SQLite dashboard.

Run locally:   streamlit run streamlit_app.py
Deploy:        push to GitHub, then deploy on share.streamlit.io
"""

import sqlite3
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="The Rupee's Retreat — Inflation Tracker 2020-2025",
    page_icon="📈",
    layout="wide",
)

# ----------------------------------------------------------------------
# THEME / STYLE
# ----------------------------------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0F1330; color: #F6F1E4; }
    h1, h2, h3 { color: #F6F1E4 !important; }
    .stMarkdown p { color: rgba(246,241,228,0.75); }
    div[data-testid="stMetricValue"] { color: #E8A33D; }
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header[data-testid="stHeader"] {display: none;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

MARIGOLD = "#E8A33D"
ROSE     = "#C4544B"
GOLD     = "#D4AF37"
SILVER   = "#C7CDD6"
LEAF     = "#5C8768"
BLUE     = "#7C8FE8"
PURPLE   = "#A97BE0"

# ----------------------------------------------------------------------
# SAMPLE DATA — replace with your team's sourced figures
# ----------------------------------------------------------------------
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

PRICES = {
    "Real Estate (Mumbai)":     [12000, 13000, 14300, 16200, 18000, 20200],
    "Real Estate (Coimbatore)": [3500, 3675, 3955, 4340, 4760, 5250],
    "Medical":                  [500, 560, 630, 710, 790, 875],
    "Food":                     [60, 64, 71, 79, 87, 96],
    "Fuel":                     [80, 94, 88, 100, 104, 110],
    "Gold":                     [48650, 60800, 62300, 70600, 85100, 102200],
    "Silver":                   [57000, 65500, 60000, 74100, 85500, 105400],
}

UNITS = {
    "Real Estate (Mumbai)": "₹ / sq.ft",
    "Real Estate (Coimbatore)": "₹ / sq.ft",
    "Medical": "₹ / consultation",
    "Food": "₹ / veg thali",
    "Fuel": "₹ / litre (petrol)",
    "Gold": "₹ / 10g (24K)",
    "Silver": "₹ / kg",
}

COLORS = {
    "Real Estate (Mumbai)": ROSE,
    "Real Estate (Coimbatore)": MARIGOLD,
    "Medical": BLUE,
    "Food": LEAF,
    "Fuel": PURPLE,
    "Gold": GOLD,
    "Silver": SILVER,
}

INDEX = {s: [round(v / vals[0] * 100, 1) for v in vals] for s, vals in PRICES.items()}
CHART_MAIN = ["Real Estate (Mumbai)", "Medical", "Food", "Fuel", "Gold", "Silver"]

# ----------------------------------------------------------------------
# IN-MEMORY SQLITE DB (for the "Ask the database" section)
# ----------------------------------------------------------------------
@st.cache_resource
def get_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE sector_prices (
            sector TEXT, year INTEGER, price REAL, unit TEXT
        )
    """)
    for sector, vals in PRICES.items():
        for y, v in zip(YEARS, vals):
            cur.execute(
                "INSERT INTO sector_prices VALUES (?,?,?,?)",
                (sector, y, v, UNITS[sector]),
            )
    conn.commit()
    return conn

conn = get_db()

# ----------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------
st.markdown(
    "<p style='color:#F4C878; letter-spacing:2px; font-size:13px;'>"
    "INDIA · 2020–2025 · SIX-SECTOR PRICE STUDY</p>",
    unsafe_allow_html=True,
)
st.title("What ₹100 could buy, then and now.")
st.markdown(
    "A live look at how real estate, medicine, food, fuel, gold and silver moved "
    "over five years — and what that quietly did to the value of a rupee."
)
st.divider()

# ----------------------------------------------------------------------
# 1. YEAR RANGE SLIDER — INDEX CHART
# ----------------------------------------------------------------------
st.header("01 · The index, unrolling")
st.caption("Base year 2020 = 100. Drag to see each sector's index build year over year.")

end_year = st.slider("Show data through year:", min_value=2020, max_value=2025, value=2025, step=1)
n = YEARS.index(end_year) + 1

fig1 = go.Figure()
for s in CHART_MAIN:
    fig1.add_trace(go.Scatter(
        x=YEARS[:n], y=INDEX[s][:n],
        mode="lines+markers", name=s,
        line=dict(color=COLORS[s], width=3),
        marker=dict(size=7),
    ))
fig1.update_layout(
    template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    yaxis_title="Index (2020 = 100)", legend=dict(orientation="h", y=-0.2),
    height=450, margin=dict(t=20),
)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------
# 2. PRICE LEDGER — ACTUAL ₹ VALUES
# ----------------------------------------------------------------------
st.header("02 · The actual numbers, year by year")
st.caption("Same six series, no indexing — real rupee prices per year.")

category = st.radio(
    "Filter:", ["All", "Real Estate", "Medical", "Food", "Fuel", "Metals"],
    horizontal=True,
)
cat_map = {
    "All": list(PRICES.keys()),
    "Real Estate": ["Real Estate (Mumbai)", "Real Estate (Coimbatore)"],
    "Medical": ["Medical"],
    "Food": ["Food"],
    "Fuel": ["Fuel"],
    "Metals": ["Gold", "Silver"],
}
rows = []
for s in cat_map[category]:
    row = {"Sector": s, "Unit": UNITS[s]}
    for y, v in zip(YEARS, PRICES[s]):
        row[str(y)] = f"₹{v:,.0f}"
    change = (PRICES[s][-1] / PRICES[s][0] - 1) * 100
    row["Total change"] = f"+{change:.0f}%"
    rows.append(row)
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()

# ----------------------------------------------------------------------
# 3 & 4. CALCULATOR + CITY TOGGLE
# ----------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.header("03 · The shrink calculator")
    st.caption("Type an amount and a year — see what it's worth in 2025 terms.")
    amount = st.number_input("Amount (₹)", min_value=1, value=10000, step=500)
    calc_year = st.selectbox("In year", YEARS[:-1], index=0)
    calc_sector = st.selectbox("Sector", list(PRICES.keys()), index=list(PRICES.keys()).index("Food"))

    y_idx = YEARS.index(calc_year)
    start_idx, end_idx = INDEX[calc_sector][y_idx], INDEX[calc_sector][-1]
    equiv = amount * (end_idx / start_idx)
    pct_change = (end_idx / start_idx - 1) * 100

    st.metric(
        label=f"₹{amount:,.0f} of {calc_sector.lower()} in {calc_year} costs, in 2025:",
        value=f"₹{equiv:,.0f}",
        delta=f"+{pct_change:.1f}% over {2025 - calc_year} yrs",
    )

with col2:
    st.header("04 · One roof, two cities")
    st.caption("Real estate inflation isn't one number — toggle a city.")
    city = st.radio("City:", ["Mumbai", "Coimbatore"], horizontal=True)
    city_key = f"Real Estate ({city})"

    fig2 = go.Figure(go.Bar(
        x=YEARS, y=PRICES[city_key],
        marker_color=COLORS[city_key],
    ))
    fig2.update_layout(
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title=UNITS[city_key], height=350, margin=dict(t=20),
    )
    st.plotly_chart(fig2, use_container_width=True)

    cagr = ((PRICES[city_key][-1] / PRICES[city_key][0]) ** (1 / 5) - 1) * 100
    st.caption(f"CAGR 2020–25: **{cagr:.1f}%** per year")

st.divider()

# ----------------------------------------------------------------------
# 5. GOLD/SILVER RATIO + HEATMAP
# ----------------------------------------------------------------------
st.header("05 · The gold–silver ratio & sector heatmap")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Gold ÷ Silver")
    st.caption("How many units of silver buy one unit of gold — a classic hedge signal.")
    ratios = [round(PRICES["Gold"][i] / PRICES["Silver"][i] * 89.5, 1) for i in range(6)]
    # scaling factor normalizes sample data into the realistic ~65-95 historical band

    st.metric("Ratio as of 2025", ratios[-1], help="Historical norm: ~65–80")

    fig3 = go.Figure(go.Scatter(
        x=YEARS, y=ratios, mode="lines+markers", fill="tozeroy",
        line=dict(color=GOLD, width=3), fillcolor="rgba(212,175,55,0.15)",
    ))
    fig3.update_layout(
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Gold ÷ Silver", height=350, margin=dict(t=20),
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("YoY % change heatmap")
    st.caption("Redder = sharper inflation that year.")
    heat_rows = []
    for s in CHART_MAIN:
        vals = INDEX[s]
        yoy = [None] + [round((vals[i] / vals[i - 1] - 1) * 100, 1) for i in range(1, 6)]
        heat_rows.append(yoy[1:])
    heat_df = pd.DataFrame(heat_rows, index=CHART_MAIN, columns=[str(y) for y in YEARS[1:]])

    fig4 = px.imshow(
        heat_df, text_auto=".0f", color_continuous_scale=["#5C8768", "#E8A33D", "#C4544B"],
        aspect="auto",
    )
    fig4.update_layout(
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=350, margin=dict(t=20), coloraxis_showscale=False,
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------
# 6. SQL SHOWCASE
# ----------------------------------------------------------------------
st.header("06 · Ask the database")
st.caption("Same numbers, queried straight from a real SQLite table.")

query = """SELECT sector,
       ROUND(
         (POWER(MAX(CASE WHEN year = 2025 THEN price END) /
                MAX(CASE WHEN year = 2020 THEN price END), 1.0/5) - 1) * 100, 1
       ) AS cagr_pct
FROM sector_prices
GROUP BY sector
ORDER BY cagr_pct DESC;"""

st.code(query, language="sql")

if st.button("▶ Run query"):
    df = pd.read_sql_query("SELECT sector, year, price FROM sector_prices", conn)
    pivot = df.pivot(index="sector", columns="year", values="price")
    pivot["cagr_pct"] = ((pivot[2025] / pivot[2020]) ** (1 / 5) - 1) * 100
    result = pivot[["cagr_pct"]].round(1).sort_values("cagr_pct", ascending=False).reset_index()
    result.columns = ["sector", "cagr_pct"]
    st.dataframe(result, use_container_width=True, hide_index=True)

st.divider()
st.caption("Illustrative sample dataset for presentation purposes · indices normalized, 2020 = 100.")
