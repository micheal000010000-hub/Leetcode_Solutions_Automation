import streamlit as st
from datetime import datetime

from ui.constants import TAB_NAMES
from ui.pages import (
    render_activity_tab,
    render_about_tab,
    render_generate_tab,
    render_git_tab,
    render_metrics_tab,
    render_queue_tab,
    render_settings_tab,
    render_sidebar_guide,
)
from ui.theme import inject_global_styles


def main() -> None:
    st.set_page_config(
        page_title="LeetCode AutoSync Studio",
        page_icon="L",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_global_styles()

    st.markdown(
        """
        <div class="hero-card">
          <h1>LeetCode AutoSync Studio</h1>
          <p class="subtle-note">Generate, monitor, and optimize your LeetCode workflow.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_sidebar_guide()

    generate_tab, queue_tab, metrics_tab, activity_tab, git_tab, settings_tab, about_tab = st.tabs(
        TAB_NAMES
    )

    with generate_tab:
        render_generate_tab()
    with queue_tab:
        render_queue_tab()
    with metrics_tab:
        render_metrics_tab()
    with activity_tab:
        render_activity_tab()
    with git_tab:
        render_git_tab()
    with settings_tab:
        render_settings_tab()
    with about_tab:
        render_about_tab()

    current_year = datetime.now().year
    st.markdown(
        f"""
        <div class="app-footer">
            <span>Copyright {current_year} LeetCode AutoSync.</span>
            <span><a href="https://wwwmichealangelo.dev/" target="_blank">Personal Website</a></span>
            <span><a href="https://github.com/micheal000010000-hub/LEETCODE-AUTOSYNC" target="_blank">Contribute to AutoSync</a></span>
            <span><a href="https://github.com/micheal000010000-hub/LEETCODE-SOLUTIONS" target="_blank">LeetCode Solutions Repo</a></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
