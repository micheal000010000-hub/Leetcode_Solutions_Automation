import streamlit as st


def inject_global_styles() -> None:
    """Apply a simple, high-contrast light theme across the full Streamlit UI."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap');

    :root {
        --bg: #f5f7fb;
        --bg-soft: #edf3fb;
        --surface: #ffffff;
        --surface-soft: #f8fbff;
        --text: #0f172a;
        --text-muted: #475569;
        --border: #d7e2ee;
        --primary: #0f766e;
        --primary-hover: #115e59;
        --primary-text: #ffffff;
        --accent-soft: #e6f5f3;
        --accent-soft-border: #a7ddd7;
        --focus-ring: #6fc8be;
        --sidebar-bg: #eef4fb;
        --shadow: rgba(15, 23, 42, 0.10);
        --info-bg: #eaf3ff;
        --info-border: #90b4e8;
        --success-bg: #eaf8ef;
        --success-border: #93d8a7;
        --warning-bg: #fff7ea;
        --warning-border: #f5c071;
        --error-bg: #ffeef0;
        --error-border: #f4a6ad;
        --tab-panel-bg: #fcfdff;
    }

    .stApp {
        font-family: 'Manrope', sans-serif;
        color: var(--text);
        background: linear-gradient(180deg, var(--bg-soft) 0%, var(--bg) 260px);
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 1.35rem;
        padding-bottom: 6rem;
    }

    h1, h2, h3, h4, h5, h6,
    p, li, label,
    [data-testid="stMarkdownContainer"],
    [data-testid="stText"],
    [data-testid="stCaptionContainer"] {
        color: var(--text) !important;
    }

    .hero-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        box-shadow: 0 10px 24px var(--shadow);
        padding: 18px 20px;
        margin-bottom: 14px;
        position: relative;
        overflow: hidden;
    }

    .hero-card::before {
        content: "";
        position: absolute;
        inset: 0 0 auto 0;
        height: 5px;
        background: linear-gradient(90deg, #0f766e, #14b8a6);
    }

    .hero-card h1 {
        margin: 0;
        font-weight: 800;
        letter-spacing: -0.02em;
    }

    .subtle-note {
        color: var(--text-muted) !important;
        margin-top: 4px;
        margin-bottom: 0;
        font-weight: 600;
    }

    button[data-baseweb="tab"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 0.55rem 1rem !important;
        margin-right: 6px;
        color: var(--text) !important;
        font-weight: 700;
        transition: all 120ms ease;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background: var(--accent-soft);
        border-color: var(--accent-soft-border);
        color: #0f4c48 !important;
    }

    [data-testid="stTabs"] [role="tablist"] {
        background: #f0f5fc;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 0.45rem 0.55rem;
        gap: 0.2rem;
    }

    [data-testid="stTabs"] [role="tabpanel"] {
        padding: 0.95rem 1rem 1.15rem;
        margin-top: 0.45rem;
        background: var(--tab-panel-bg);
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="select"] > div {
        background: var(--surface) !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        caret-color: var(--text) !important;
    }

    [data-baseweb="input"] input::placeholder,
    [data-baseweb="textarea"] textarea::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        opacity: 1 !important;
    }

    [data-baseweb="input"] input:focus,
    [data-baseweb="textarea"] textarea:focus,
    [data-baseweb="select"] > div:focus-within {
        border-color: var(--focus-ring) !important;
        box-shadow: 0 0 0 1px var(--focus-ring) !important;
    }

    /* ── Element toolbar (dataframe hover: search / download / fullscreen) ── */
    /* Only fix icon colour — do NOT re-box the container */
    [data-testid="stElementToolbar"] button,
    [data-testid="stElementToolbarButton"] {
        color: var(--text) !important;
        background: transparent !important;
    }

    [data-testid="stElementToolbar"] button:hover,
    [data-testid="stElementToolbar"] button:focus-visible,
    [data-testid="stElementToolbar"] button[aria-expanded="true"],
    [data-testid="stElementToolbarButton"]:hover,
    [data-testid="stElementToolbarButton"]:focus-visible,
    [data-testid="stElementToolbarButton"][aria-expanded="true"] {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    [data-testid="stElementToolbar"] button:hover *,
    [data-testid="stElementToolbar"] button:focus-visible *,
    [data-testid="stElementToolbar"] button[aria-expanded="true"] *,
    [data-testid="stElementToolbarButton"]:hover *,
    [data-testid="stElementToolbarButton"]:focus-visible *,
    [data-testid="stElementToolbarButton"][aria-expanded="true"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    [data-testid="stElementToolbar"] svg,
    [data-testid="stElementToolbarButton"] svg {
        fill: var(--text) !important;
        color: var(--text) !important;
    }

    [data-testid="stElementToolbar"] button:hover svg,
    [data-testid="stElementToolbar"] button:focus-visible svg,
    [data-testid="stElementToolbar"] button[aria-expanded="true"] svg,
    [data-testid="stElementToolbarButton"]:hover svg,
    [data-testid="stElementToolbarButton"]:focus-visible svg,
    [data-testid="stElementToolbarButton"][aria-expanded="true"] svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    /* ── BaseWeb popover (dataframe column filter, multiselect dropdown) ── */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="popover"] ul,
    [data-baseweb="popover"] li {
        background: var(--surface) !important;
        color: var(--text) !important;
    }

    [data-baseweb="popover"] input,
    [data-baseweb="popover"] textarea {
        background: var(--surface) !important;
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
        border: 1px solid var(--border) !important;
        caret-color: var(--text) !important;
    }

    /* ── BaseWeb menu (option list for selects / column filter / multiselect) ── */
    [data-baseweb="menu"],
    [data-baseweb="menu"] ul {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px var(--shadow) !important;
    }

    [data-baseweb="menu"] li,
    [data-baseweb="menu"] [role="option"] {
        background: var(--surface) !important;
        color: var(--text) !important;
    }

    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] [role="option"]:hover {
        background: var(--accent-soft) !important;
        color: var(--text) !important;
    }

    /* ── ListBox / generic option ── */
    [role="listbox"],
    [role="option"] {
        background: var(--surface) !important;
        color: var(--text) !important;
    }

    [role="option"][aria-selected="true"] {
        background: #c2410c !important;
        color: #ffffff !important;
    }

    [role="option"][aria-selected="true"] * {
        color: #ffffff !important;
    }

    [data-baseweb="tag"] {
        background: #c2410c !important;
        border-color: #9a3412 !important;
    }

    [data-baseweb="tag"] *,
    [data-baseweb="tag"] span,
    [data-baseweb="tag"] svg {
        color: #ffffff !important;
        fill: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    .stButton button,
    .stDownloadButton button,
    .stForm button,
    .stFormSubmitButton button,
    [data-testid="stFormSubmitButton"] button,
    [data-testid="stBaseButton-primary"],
    [data-testid="stBaseButton-secondary"],
    button[kind="primary"],
    button[kind="secondary"] {
        background: var(--primary);
        color: var(--primary-text) !important;
        -webkit-text-fill-color: var(--primary-text) !important;
        border: 1px solid var(--primary);
        border-radius: 10px;
        font-weight: 700;
        transition: all 120ms ease;
    }

    .stButton button span,
    .stDownloadButton button span,
    .stForm button span,
    .stFormSubmitButton button span,
    [data-testid="stFormSubmitButton"] button span,
    [data-testid="stBaseButton-primary"] span,
    [data-testid="stBaseButton-secondary"] span {
        color: var(--primary-text) !important;
        -webkit-text-fill-color: var(--primary-text) !important;
    }

    .stButton button:hover,
    .stDownloadButton button:hover,
    .stForm button:hover,
    .stFormSubmitButton button:hover,
    [data-testid="stFormSubmitButton"] button:hover,
    [data-testid="stBaseButton-primary"]:hover,
    [data-testid="stBaseButton-secondary"]:hover {
        background: var(--primary-hover);
        border-color: var(--primary-hover);
        color: var(--primary-text) !important;
        -webkit-text-fill-color: var(--primary-text) !important;
    }

    .stButton button:focus,
    .stDownloadButton button:focus,
    .stForm button:focus,
    .stFormSubmitButton button:focus,
    [data-testid="stFormSubmitButton"] button:focus {
        color: var(--primary-text) !important;
        -webkit-text-fill-color: var(--primary-text) !important;
    }

    [data-testid="stForm"],
    [data-testid="stMetric"],
    [data-testid="stCodeBlock"],
    [data-testid="stDataFrame"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        box-shadow: 0 6px 16px var(--shadow);
    }

    [data-testid="stForm"] {
        padding: 1rem 1rem 0.7rem !important;
    }

    [data-testid="stMetric"] {
        padding: 0.85rem 1rem !important;
        min-height: 5.2rem;
    }

    [data-testid="stDataFrame"] {
        padding: 0.4rem !important;
    }

    [data-testid="stCodeBlock"] {
        padding: 0.55rem !important;
    }

    [data-testid="stDataFrame"] * {
        color: var(--text) !important;
    }

    [data-testid="stCodeBlock"] pre,
    [data-testid="stCodeBlock"] code {
        color: var(--text) !important;
        background: var(--surface-soft) !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-weight: 700;
    }

    [data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }

    [data-testid="stSidebar"] * {
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="input"] input,
    [data-testid="stSidebar"] [data-baseweb="textarea"] textarea {
        background: var(--surface) !important;
        color: var(--text) !important;
    }

    [data-testid="stSidebar"] code,
    code {
        color: var(--text) !important;
        background: var(--bg-soft) !important;
        border-radius: 6px;
        padding: 0.1rem 0.35rem;
    }

    [data-testid="stInfo"] {
        background: var(--info-bg) !important;
        border: 1px solid var(--info-border) !important;
    }

    [data-testid="stSuccess"] {
        background: var(--success-bg) !important;
        border: 1px solid var(--success-border) !important;
    }

    [data-testid="stWarning"] {
        background: var(--warning-bg) !important;
        border: 1px solid var(--warning-border) !important;
    }

    [data-testid="stError"] {
        background: var(--error-bg) !important;
        border: 1px solid var(--error-border) !important;
    }

    a {
        color: #0f766e !important;
        text-decoration: none;
        font-weight: 700;
    }

    a:hover {
        color: #115e59 !important;
        text-decoration: underline;
    }

    .app-footer {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 999;
        margin: 0;
        padding: 0.85rem 1rem;
        background: var(--sidebar-bg);
        border-top: 1px solid var(--border);
        border-radius: 0;
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem 1rem;
        align-items: center;
        justify-content: center;
        color: var(--text);
        font-size: 0.92rem;
        font-weight: 600;
    }

    .app-footer a {
        color: #0f766e !important;
        font-weight: 700;
    }

    @media (max-width: 900px) {
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1.5rem;
        }

        .hero-card {
            padding: 14px 14px;
        }

        .hero-card h1 {
            font-size: 1.35rem;
        }

        h2 {
            font-size: 1.12rem;
        }
    }

    /* ── Tooltips: MUST be last — overrides the broad stDataFrame * rule above ── */
    [role="tooltip"] {
        background: #1e293b !important;
        border: none !important;
        border-radius: 6px !important;
    }

    [role="tooltip"],
    [role="tooltip"] *,
    [role="tooltip"] span,
    [role="tooltip"] div,
    [role="tooltip"] p,
    [role="tooltip"] label {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background: transparent !important;
        border: none !important;
    }

    /* Re-apply dark bg on the container only (overridden by transparent above) */
    [role="tooltip"] { background: #1e293b !important; }

    </style>
    """

    st.markdown(css, unsafe_allow_html=True)
