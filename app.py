from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="SPX Execution Dashboard",
    page_icon="📈",
    layout="wide",
)

DEFAULT_JSON = Path("data/spx_execution_report.json")


def load_report(uploaded_file) -> dict[str, Any]:
    if uploaded_file is not None:
        return json.load(uploaded_file)
    if DEFAULT_JSON.exists():
        return json.loads(DEFAULT_JSON.read_text(encoding="utf-8"))
    return {"execution_model": {}, "trigger_rules": {}, "actionable_intelligence": []}


def fmt_num(value: Any, pct: bool = False) -> str:
    try:
        if value is None:
            return "n/a"
        value = float(value)
        if pct:
            return f"{value:.2%}"
        return f"{value:,.4f}" if abs(value) < 100 else f"{value:,.2f}"
    except Exception:
        return str(value)


def bool_badge(value: Any) -> str:
    if value is True:
        return "✅ True"
    if value is False:
        return "⚪ False"
    return f"— {value}"


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
    fig.update_layout(height=220, margin=dict(l=20, r=20, t=45, b=10))
    return fig


def make_trigger_table(trigger_rules: dict[str, Any]) -> pd.DataFrame:
    ordered = [
        "actionable", "setup_type", "entry_rule", "entry_price", "stop_price",
        "target_price", "invalid_if", "participation_score", "participation_quality",
        "execution_state", "execution_readiness", "volume_spike", "buy_ratio",
        "trade_flow_bias", "trade_flow_bias_recent", "velocity_1m", "velocity_5m",
        "momentum_state", "slippage_guard_ok", "false_start_guard_ok",
        "downside_persistence_confirmed", "long_persistence_confirmed",
        "retest_failure_confirmed", "failed_long_short_bias_candidate", "notes",
    ]
    rows = []
    for k in ordered:
        if k in trigger_rules:
            rows.append({"Metric": k, "Value": trigger_rules[k]})
    for k, v in trigger_rules.items():
        if k not in ordered:
            rows.append({"Metric": k, "Value": v})
    return pd.DataFrame(rows)


def parse_story(story_lines: list[str]) -> list[str]:
    cleaned = []
    for line in story_lines:
        if line and not line.startswith("====="):
            cleaned.append(line)
    return cleaned


st.title("SPX Execution Dashboard")
st.caption("GitHub/Streamlit-ready visualization for the SPX execution report JSON.")

with st.sidebar:
    st.header("Data Source")
    uploaded = st.file_uploader("Upload spx_execution_report.json", type=["json"])
    use_sample = st.checkbox("Use bundled sample JSON", value=uploaded is None)
    if use_sample and uploaded is not None:
        st.info("Uploaded file takes priority.")
    st.markdown("---")
    st.write("Expected file path for sample data:")
    st.code(str(DEFAULT_JSON))
    st.write("This app visualizes the JSON output from the notebook’s final report cell.")

report = load_report(uploaded if uploaded is not None else (None if use_sample else None))
execution = report.get("execution_model", {})
trigger = report.get("trigger_rules", {})
story = parse_story(report.get("actionable_intelligence", []))

if not execution and not trigger:
    st.warning("No report JSON found. Upload a JSON file or add data/spx_execution_report.json.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Structural Bias", execution.get("structural_bias", "n/a"))
c2.metric("Execution State", execution.get("execution_state", execution.get("alert_state", "n/a")))
c3.metric("Execution Readiness", execution.get("execution_readiness", "n/a"))
c4.metric("Run Time", report.get("run_date_time", "n/a"))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Gamma Regime", execution.get("gamma_regime", "n/a"))
c2.metric("SMA Regime", execution.get("sma_regime", "n/a"))
c3.metric("VWAP Position", execution.get("vwap_position", "n/a"))
c4.metric("Volatility", execution.get("volatility", "n/a"))

st.markdown("### Participation & Execution Quality")
g1, g2, g3 = st.columns(3)
with g1:
    st.plotly_chart(gauge(trigger.get("participation_score", 0), "Participation Score"), use_container_width=True)
with g2:
    st.plotly_chart(gauge(trigger.get("pin_pressure", 0), "Pin Pressure"), use_container_width=True)
with g3:
    st.plotly_chart(gauge(trigger.get("volume_component", 0), "Volume Component"), use_container_width=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Actionable", "Yes" if trigger.get("actionable") else "No")
c2.metric("Participation Confirmed", "Yes" if trigger.get("participation_confirmed") else "No")
c3.metric("Momentum State", trigger.get("momentum_state", "n/a"))
c4.metric("Participation Quality", trigger.get("participation_quality", "n/a"))

st.markdown("### Key Trade Levels")
c1, c2, c3 = st.columns(3)
c1.metric("Entry Price", fmt_num(trigger.get("entry_price")))
c2.metric("Stop Price", fmt_num(trigger.get("stop_price")))
c3.metric("Target Price", fmt_num(trigger.get("target_price")))

st.markdown("### Trigger Summary")
st.info(trigger.get("entry_rule", "n/a"))
st.warning(trigger.get("invalid_if", "n/a"))

st.markdown("### Precision Guards")
g1, g2, g3, g4 = st.columns(4)
g1.write("Slippage Guard")
g1.write(bool_badge(trigger.get("slippage_guard_ok")))
g2.write("False-Start Guard")
g2.write(bool_badge(trigger.get("false_start_guard_ok")))
g3.write("Downside Persistence")
g3.write(bool_badge(trigger.get("downside_persistence_confirmed")))
g4.write("Long Persistence")
g4.write(bool_badge(trigger.get("long_persistence_confirmed")))

st.markdown("### Trigger Metrics")
df = make_trigger_table(trigger)
st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("### Actionable Intelligence")
for line in story:
    if line.startswith("Top 5 Levels By Hedging Impact:"):
        st.markdown("**Top 5 Levels By Hedging Impact**")
    else:
        st.write(line)

st.markdown("### Raw JSON")
st.json(report, expanded=False)
