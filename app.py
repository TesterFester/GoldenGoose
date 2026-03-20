from __future__ import annotations

import json
import os
from datetime import datetime, time
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from spx_engine import run_model

st.set_page_config(page_title="SPX Live Execution Dashboard", page_icon="📈", layout="wide")

NY = pytz.timezone("America/New_York")
SAMPLE_JSON = Path("data/spx_execution_report.json")


def now_ny() -> datetime:
    return datetime.now(NY)


def current_refresh_schedule_seconds() -> int | None:
    now = now_ny()
    if now.weekday() >= 5:
        return None
    t = now.time()
    # Testing schedule: refresh every 2 minutes during market hours only
    if time(9, 30) <= t < time(16, 0):
        return 120
    return None


def fmt_num(value: Any) -> str:
    try:
        if value is None:
            return "n/a"
        x = float(value)
        if abs(x) >= 100:
            return f"{x:,.2f}"
        return f"{x:,.4f}"
    except Exception:
        return str(value)


def gauge(value: float, title: str, max_value: float = 1.0) -> go.Figure:
    value = max(0.0, min(float(value), max_value))
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"valueformat": ".2f"},
            title={"text": title},
            gauge={
                "axis": {"range": [0, max_value]},
                "bar": {"thickness": 0.3},
                "steps": [
                    {"range": [0, 0.35 * max_value], "color": "#f3d1d1"},
                    {"range": [0.35 * max_value, 0.65 * max_value], "color": "#f3e7c7"},
                    {"range": [0.65 * max_value, max_value], "color": "#d7efd7"},
                ],
            },
        )
    )
    fig.update_layout(height=220, margin=dict(l=15, r=15, t=40, b=10))
    return fig


def get_api_key() -> str:
    try:
        if "POLYGON_API_KEY" in st.secrets:
            return st.secrets["POLYGON_API_KEY"]
    except Exception:
        pass
    return os.environ.get("POLYGON_API_KEY", "")


def load_sample() -> dict[str, Any]:
    if SAMPLE_JSON.exists():
        return json.loads(SAMPLE_JSON.read_text(encoding="utf-8"))
    return {"execution_model": {}, "trigger_rules": {}, "actionable_intelligence": [], "run_date_time": ""}


def make_table(trigger_rules: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame([{"Metric": k, "Value": v} for k, v in trigger_rules.items()])


st.title("SPX Live Execution Dashboard")
st.caption("Live Polygon-powered Streamlit app with scheduled auto-refresh during market hours.")

schedule = current_refresh_schedule_seconds()

with st.sidebar:
    st.header("Live Controls")
    api_key_present = bool(get_api_key())
    st.write("Polygon API key detected:" , "✅" if api_key_present else "❌")
    if schedule is None:
        st.info("Auto-refresh is off outside market hours.")
    else:
        st.info(f"Auto-refresh active every {schedule} seconds.")
    use_live = st.toggle("Run live model", value=api_key_present, disabled=not api_key_present)
    live_trading_mode = st.toggle("Live trading mode", value=True)
    refresh_now = st.button("Refresh now")
    uploaded = st.file_uploader("Optional override JSON", type=["json"])
    st.markdown("---")
    st.write("Refresh schedule (NY time):")
    st.write("- 9:30 AM–4:00 PM: every 120s (testing mode)")
    st.write("- Outside market hours: off")

if schedule is not None:
    st_autorefresh(interval=schedule * 1000, key=f"auto_refresh_{schedule}")

if refresh_now:
    st.rerun()

report = None
state = {}

if uploaded is not None:
    report = json.load(uploaded)
elif use_live and api_key_present:
    try:
        with st.spinner("Running live SPX model..."):
            report, state = run_model(api_key=get_api_key(), live_trading_mode=live_trading_mode)
    except Exception as e:
        st.error(f"Live model run failed: {e}")
        st.info("Showing bundled sample JSON instead.")
        report = load_sample()
else:
    report = load_sample()

execution = report.get("execution_model", {})
trigger = report.get("trigger_rules", {})
story = [x for x in report.get("actionable_intelligence", []) if x and not x.startswith("=====")]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Structural Bias", execution.get("structural_bias", "n/a"))
c2.metric("Execution State", execution.get("execution_state", execution.get("alert_state", "n/a")))
c3.metric("Execution Readiness", execution.get("execution_readiness", "n/a"))
c4.metric("Run Date and Time", report.get("run_date_time", "n/a"))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Gamma Regime", execution.get("gamma_regime", "n/a"))
c2.metric("SMA Regime", execution.get("sma_regime", "n/a"))
c3.metric("VWAP Position", execution.get("vwap_position", "n/a"))
c4.metric("Volatility", execution.get("volatility", "n/a"))

st.markdown("### Participation & Quality")
g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(gauge(trigger.get("participation_score", 0), "Participation Score"), use_container_width=True)
with g2:
    st.plotly_chart(gauge(trigger.get("pin_pressure", 0), "Pin Pressure"), use_container_width=True)
with g3:
    st.plotly_chart(gauge(trigger.get("volume_component", 0), "Volume Component"), use_container_width=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Actionable", "Yes" if trigger.get("actionable") else "No")
m2.metric("Participation Confirmed", "Yes" if trigger.get("participation_confirmed") else "No")
m3.metric("Momentum State", trigger.get("momentum_state", "n/a"))
m4.metric("Participation Quality", trigger.get("participation_quality", "n/a"))

st.markdown("### Trade Levels")
t1, t2, t3 = st.columns(3)
t1.metric("Entry Price", fmt_num(trigger.get("entry_price")))
t2.metric("Stop Price", fmt_num(trigger.get("stop_price")))
t3.metric("Target Price", fmt_num(trigger.get("target_price")))

st.markdown("### Trigger Summary")
st.info(trigger.get("entry_rule", "n/a"))
st.warning(trigger.get("invalid_if", "n/a"))

st.markdown("### Precision Guards")
p1, p2, p3, p4 = st.columns(4)
p1.metric("Slippage Guard", str(trigger.get("slippage_guard_ok")))
p2.metric("False-Start Guard", str(trigger.get("false_start_guard_ok")))
p3.metric("Downside Persistence", str(trigger.get("downside_persistence_confirmed")))
p4.metric("Long Persistence", str(trigger.get("long_persistence_confirmed")))

st.markdown("### Actionable Intelligence")
for line in story:
    st.write(line)

st.markdown("### Trigger Rules Table")
if trigger:
    st.dataframe(make_table(trigger), use_container_width=True, hide_index=True)

with st.expander("Raw JSON", expanded=False):
    st.json(report, expanded=False)

with st.expander("Live run diagnostics", expanded=False):
    st.write("Current New York time:", now_ny().strftime("%Y-%m-%d %H:%M:%S %Z"))
    st.write("Auto-refresh schedule (seconds):", schedule if schedule is not None else "off")
    st.write("Live mode:", use_live)
