from datetime import datetime
from typing import Dict, List

import pandas as pd
import streamlit as st


MAX_ACTIVITY_ROWS = 300


def _default_events() -> List[Dict[str, str]]:
    return []


def init_activity_state() -> None:
    if "activity_events" not in st.session_state:
        st.session_state["activity_events"] = _default_events()


def add_activity_event(action: str, status: str, details: str = "", category: str = "general") -> None:
    init_activity_state()
    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "category": category,
        "action": action,
        "status": status,
        "details": details,
    }
    st.session_state["activity_events"].insert(0, event)
    st.session_state["activity_events"] = st.session_state["activity_events"][:MAX_ACTIVITY_ROWS]


def get_activity_dataframe() -> pd.DataFrame:
    init_activity_state()
    events = st.session_state.get("activity_events", [])
    if not events:
        return pd.DataFrame(columns=["timestamp", "category", "action", "status", "details"])
    return pd.DataFrame(events)
