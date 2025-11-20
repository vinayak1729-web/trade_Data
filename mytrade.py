import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ========================= CONFIG =========================
st.set_page_config(page_title="P&L Dashboard", layout="wide")
st.title("Profit & Loss Dashboard")

# Your public CSV export link (make sure sheet is shared as "Anyone with the link")
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zTHvaqMY3LIYeqoCpOgwUlptRZ1JIEgU2wD2gybMLns/export?format=csv&gid=0"

# ========================= FORCE REFRESH BUTTON =========================
if st.button("Refresh Data Now – Get Latest Updates", type="primary", use_container_width=True):
    st.cache_data.clear()   # This clears the cache instantly
    st.success("Data refreshed successfully!")
    st.rerun()               # Reload the app with fresh data

# ========================= LOAD DATA =========================
@st.cache_data(ttl=600)  # normal cache = 10 min, but button bypasses it
def load_data():
    df = pd.read_csv(SHEET_URL)
    df.columns = [c.strip() for c in df.columns]
    
    # Handle date format like "11 Nov"
    df["date"] = pd.to_datetime(df["date"], format="%d %b", dayfirst=True)
    df = df.sort_values("date").reset_index(drop=True)
    
    # Clean numbers (remove commas)
    for col in ["money in", "gain/loss", "money out", "overall money"]:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
    
    return df

df = load_data()

# ========================= MAIN P&L CHART =========================
st.subheader("Daily Profit & Loss + Cumulative Balance")

fig = go.Figure()

# Daily P&L bars
fig.add_trace(go.Bar(
    x=df["date"],
    y=df["gain/loss"],
    name="Daily P&L",
    marker_color=df["gain/loss"].apply(lambda x: "#00d4aa" if x >= 0 else "#ff3b30"),
    text=df["gain/loss"].apply(lambda x: f"₹{x:,.0f}"),
    textposition="outside"
))

# Cumulative balance line
fig.add_trace(go.Scatter(
    x=df["date"],
    y=df["overall money"],
    mode="lines+markers+text",
    name="Running Balance",
    line=dict(color="#9b59b6", width=5),
    marker=dict(size=10),
    text=df["overall money"],
    textposition="top center",
    textfont=dict(size=12)
))

fig.update_layout(
    height=650,
    barmode="relative",
    xaxis_title="",
    yaxis_title="Amount (₹)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ========================= METRICS =========================
c1, c2, c3, c4 = st.columns(4)

total_pnl = df["gain/loss"].sum()
current = df["overall money"].iloc[-1]
best = df.loc[df["gain/loss"].idxmax()]
worst = df.loc[df["gain/loss"].idxmin()]

c1.metric("Total P&L", f"₹{total_pnl:,.0f}", delta=f"₹{total_pnl:,.0f}")
c2.metric("Current Balance", f"₹{current:,.0f}")
c3.metric("Best Day", f"₹{best['gain/loss']:,.0f}", delta=best["date"].strftime("%d %b"))
c4.metric("Worst Day", f"₹{worst['gain/loss']:,.0f}", delta=worst["date"].strftime("%d %b"))

# ========================= SECONDARY (collapsed) =========================
with st.expander("Money In / Out Details", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Money In**")
        st.bar_chart(df.set_index("date")["money in"], height=250, use_container_width=True)
        st.write(f"Total In: ₹{df['money in'].sum():,.0f}")
    with col2:
        st.write("**Money Out**")
        st.bar_chart(df.set_index("date")["money out"], height=250, use_container_width=True)
        st.write(f"Total Out: ₹{df['money out'].sum():,.0f}")

# ========================= FOOTER =========================
st.caption(f"Data last refreshed: {datetime.now().strftime('%d %b %Y, %H:%M:%S')}")