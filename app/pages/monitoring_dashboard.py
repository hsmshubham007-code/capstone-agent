import time

import pandas as pd
import requests
import streamlit as st

API_URL = st.sidebar.text_input(
    "🔗 API URL",
    "http://localhost:8000",
)

REFRESH_SECONDS = st.sidebar.number_input(
    "🔄 Refresh interval (seconds)",
    min_value=5,
    max_value=300,
    value=10,
)


def get_json(endpoint):
    """Get JSON data from the FastAPI backend."""

    try:
        response = requests.get(
            f"{API_URL}{endpoint}",
            timeout=5,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as exc:
        st.error(
            f"❌ Unable to connect to API: {exc}"
        )
        return None


# ============================================================
# PAGE HEADER
# ============================================================

st.title("📊 Monitoring Dashboard")

st.caption(
    "📡 Live operational metrics from the "
    "FastAPI Company Policy Agent"
)


# ============================================================
# FETCH SYSTEM DATA
# ============================================================

health = get_json("/health")
ready = get_json("/ready")
metrics = get_json("/metrics")


if (
    health is None
    or ready is None
    or metrics is None
):
    st.stop()


# ============================================================
# SYSTEM HEALTH
# ============================================================

st.markdown("## 🏥 System Health")

health_col, ready_col = st.columns(2)

with health_col:

    if health.get("status") in (
        "healthy",
        "ok",
    ):

        st.success(
            "✅ API Health: Healthy"
        )

    else:

        st.error(
            "❌ API Health: Unhealthy"
        )


with ready_col:

    if ready.get("status") in (
        "ready",
        "ok",
    ):

        st.success(
            "✅ API Readiness: Ready"
        )

    else:

        st.error(
            "❌ API Readiness: Not Ready"
        )


# ============================================================
# EXTRACT METRICS
# ============================================================

counters = metrics.get(
    "counters",
    {},
)

latency = metrics.get(
    "latency",
    {},
)

llm = metrics.get(
    "llm",
    {},
)

cost = metrics.get(
    "cost",
    {},
)


# ============================================================
# REQUEST METRICS
# ============================================================

total_requests = counters.get(
    "requests_total",
    0,
)

total_errors = counters.get(
    "requests_errors_total",
    0,
)

successful_requests = max(
    total_requests - total_errors,
    0,
)

success_rate = (
    successful_requests
    / total_requests
    * 100
    if total_requests
    else 0
)


st.markdown("## 📈 Request Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "📨 Total Requests",
        total_requests,
    )

with col2:

    st.metric(
        "✅ Successful",
        successful_requests,
    )

with col3:

    st.metric(
        "❌ Errors",
        total_errors,
    )

with col4:

    st.metric(
        "🎯 Success Rate",
        f"{success_rate:.2f}%",
    )


# ============================================================
# LATENCY
# ============================================================

st.markdown("## ⏱️ Latency")

lat1, lat2, lat3, lat4 = st.columns(4)

with lat1:

    st.metric(
        "📊 Average",
        f"{latency.get('average_ms', 0):.2f} ms",
    )

with lat2:

    st.metric(
        "📍 P50",
        f"{latency.get('p50_ms', 0):.2f} ms",
    )

with lat3:

    st.metric(
        "📈 P95",
        f"{latency.get('p95_ms', 0):.2f} ms",
    )

with lat4:

    st.metric(
        "⚡ Last Request",
        f"{latency.get('last_ms', 0):.2f} ms",
    )


# ============================================================
# ERROR RATE
# ============================================================

st.markdown("## 🚨 Error Rate")

error_rate = metrics.get(
    "error_rate",
    0,
)

st.progress(
    min(
        max(error_rate, 0),
        1.0,
    )
)

st.write(
    f"📉 Current error rate: "
    f"**{error_rate * 100:.2f}%**"
)


# ============================================================
# LLM USAGE
# ============================================================

st.markdown("## 🤖 LLM Usage")

llm1, llm2, llm3, llm4 = st.columns(4)

with llm1:

    st.metric(
        "🤖 LLM Requests",
        llm.get(
            "requests",
            0,
        ),
    )

with llm2:

    st.metric(
        "⬆️ Prompt Tokens",
        f"{llm.get('prompt_tokens', 0):,}",
    )

with llm3:

    st.metric(
        "⬇️ Completion Tokens",
        f"{llm.get('completion_tokens', 0):,}",
    )

with llm4:

    st.metric(
        "🔢 Total Tokens",
        f"{llm.get('total_tokens', 0):,}",
    )


# ============================================================
# COST
# ============================================================

st.markdown("## 💰 Cost")

cost1, cost2, cost3 = st.columns(3)

with cost1:

    st.metric(
        "💵 Total Cost",
        f"${cost.get('total_usd', 0):.6f}",
    )

with cost2:

    st.metric(
        "💳 Cost / Request",
        f"${cost.get('cost_per_request_usd', 0):.6f}",
    )

with cost3:

    st.metric(
        "🧾 Requests With Cost",
        cost.get(
            "requests_with_cost",
            0,
        ),
    )


# ============================================================
# APPLICATION COUNTERS
# ============================================================

st.markdown("## 📊 Application Counters")

if counters:

    counter_data = pd.DataFrame(
        [
            {
                "📌 Metric": key,
                "🔢 Value": value,
            }
            for key, value in counters.items()
        ]
    )

    st.dataframe(
        counter_data,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "ℹ️ No application counters "
        "recorded yet."
    )


# ============================================================
# RAW METRICS
# ============================================================

with st.expander(
    "🔍 View Raw Metrics"
):

    st.json(metrics)


# ============================================================
# AUTO REFRESH
# ============================================================

st.caption(
    f"🔄 Dashboard refreshes every "
    f"{REFRESH_SECONDS} seconds."
)

time.sleep(
    REFRESH_SECONDS
)

st.rerun()