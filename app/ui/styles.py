"""
ECDAT Stitch Design System — Custom CSS & Typography Tokens.
Source of Truth: Stitch Project 'ECDAT Security Workstation' (ID: 15951502437945520827).
Palette: Dark charcoal surfaces (#0f141b, #171c23, #252a32), amber accents (#ffc174, #f59e0b),
subtle borders (#30353d, #534434), and monospace technical information (JetBrains Mono).
"""

STITCH_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">

<style>
    /* =========================================================================
       GLOBAL RESET & THEME TOKENS
       ========================================================================= */
    :root {
        --stitch-bg: #0f141b;
        --stitch-surface-lowest: #090f15;
        --stitch-surface-low: #171c23;
        --stitch-surface-mid: #1b2027;
        --stitch-surface-high: #252a32;
        --stitch-surface-highest: #30353d;
        --stitch-outline: #30353d;
        --stitch-outline-variant: #534434;
        --stitch-primary: #ffc174;
        --stitch-primary-container: #f59e0b;
        --stitch-on-primary-container: #472a00;
        --stitch-text: #dee2ec;
        --stitch-text-muted: #94a3b8;
        --stitch-tertiary: #6de575;
        --stitch-error: #ffb4ab;
        --stitch-error-container: #93000a;
        --stitch-secondary: #a2c9ff;
    }

    /* Overall App Viewport */
    .stApp {
        background-color: var(--stitch-bg) !important;
        color: var(--stitch-text) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Reduce default top padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }

    /* Hide default Streamlit deploy/menu clutter */
    #MainMenu, header[data-testid="stHeader"], footer {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Subtle custom scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #090f15;
    }
    ::-webkit-scrollbar-thumb {
        background: #30353d;
        border-radius: 2px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #534434;
    }

    /* =========================================================================
       SIDEBAR NAVIGATION
       ========================================================================= */
    section[data-testid="stSidebar"] {
        background-color: var(--stitch-surface-lowest) !important;
        border-right: 1px solid var(--stitch-outline) !important;
        min-width: 260px !important;
        max-width: 275px !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1rem !important;
    }

    /* Sidebar Radio List Styling as Stitch Tabs */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        gap: 2px !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label {
        background-color: transparent !important;
        border: 1px solid transparent !important;
        border-radius: 2px !important;
        padding: 6px 10px !important;
        color: #94a3b8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background-color: var(--stitch-surface-low) !important;
        color: var(--stitch-text) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-checked="true"],
    section[data-testid="stSidebar"] div[data-testid="stRadio"] label:has(input:checked) {
        background-color: var(--stitch-surface-high) !important;
        border-left: 2px solid var(--stitch-primary-container) !important;
        color: var(--stitch-primary) !important;
        font-weight: 600 !important;
    }

    /* Hide the radio circle icon */
    section[data-testid="stSidebar"] div[data-testid="stRadio"] input[type="radio"] {
        display: none !important;
    }

    /* =========================================================================
       CUSTOM TOP BAR
       ========================================================================= */
    .stitch-topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: var(--stitch-surface-lowest);
        border: 1px solid var(--stitch-outline);
        border-radius: 4px;
        padding: 6px 14px;
        margin-bottom: 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
    }

    .stitch-topbar-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .stitch-topbar-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .stitch-brand {
        color: var(--stitch-primary);
        font-weight: 700;
        letter-spacing: -0.01em;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* =========================================================================
       CARD CONTAINERS & PANELS
       ========================================================================= */
    .stitch-card {
        background-color: var(--stitch-surface-low);
        border: 1px solid var(--stitch-outline);
        border-radius: 4px;
        padding: 14px 16px;
        margin-bottom: 14px;
    }

    .stitch-card-lowest {
        background-color: var(--stitch-surface-lowest);
        border: 1px solid var(--stitch-surface-high);
        border-radius: 4px;
        padding: 12px 14px;
        margin-bottom: 12px;
    }

    .stitch-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid var(--stitch-outline);
        padding-bottom: 8px;
        margin-bottom: 12px;
    }

    .stitch-card-title {
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        font-weight: 600;
        color: var(--stitch-text);
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .stitch-card-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: var(--stitch-text-muted);
    }

    /* Metric Cards */
    .stitch-metric-box {
        background-color: var(--stitch-surface-low);
        border: 1px solid var(--stitch-outline);
        border-radius: 4px;
        padding: 12px 14px;
        position: relative;
    }

    .stitch-metric-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
        color: var(--stitch-text-muted);
        letter-spacing: 0.06em;
        margin-bottom: 4px;
    }

    .stitch-metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 700;
        color: var(--stitch-primary);
        line-height: 1.1;
    }

    .stitch-metric-desc {
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        color: var(--stitch-text-muted);
        margin-top: 4px;
    }

    /* =========================================================================
       BADGES & PILLS
       ========================================================================= */
    .stitch-badge {
        display: inline-flex;
        align-items: center;
        padding: 2px 7px;
        border-radius: 2px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        line-height: 1.2;
    }

    .badge-critical { background-color: #991b1b; color: #ffffff; border: 1px solid #ef4444; }
    .badge-high     { background-color: #9a3412; color: #ffffff; border: 1px solid #f97316; }
    .badge-med      { background-color: #78350f; color: #ffffff; border: 1px solid #f59e0b; }
    .badge-low      { background-color: #064e3b; color: #ffffff; border: 1px solid #10b981; }
    .badge-info     { background-color: #1e293b; color: #94a3b8; border: 1px solid #475569; }

    .badge-shor     { background-color: #450a0a; color: #fca5a5; border: 1px solid #ef4444; }
    .badge-grover   { background-color: #451a03; color: #fdba74; border: 1px solid #f59e0b; }
    .badge-safe     { background-color: #052e16; color: #86efac; border: 1px solid #22c55e; }
    .badge-broken   { background-color: #3b0764; color: #f472b6; border: 1px solid #d946ef; }

    .badge-hndl     { background-color: #7f1d1d; color: #fecaca; border: 1px solid #dc2626; font-weight: 700; }
    .badge-tnfl     { background-color: #78350f; color: #fef08a; border: 1px solid #d97706; font-weight: 700; }

    /* =========================================================================
       TERMINAL VIEWER
       ========================================================================= */
    .stitch-terminal {
        background-color: #06090e;
        border: 1px solid var(--stitch-outline);
        border-radius: 4px;
        padding: 12px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        line-height: 1.5;
        color: #cbd5e1;
        max-height: 480px;
        overflow-y: auto;
    }

    .stitch-terminal-line {
        display: flex;
        gap: 8px;
        margin-bottom: 2px;
    }

    .stitch-term-time { color: #64748b; }
    .stitch-term-info { color: #38bdf8; }
    .stitch-term-warn { color: #f59e0b; }
    .stitch-term-err  { color: #ef4444; }
    .stitch-term-succ { color: #4ade80; }

    /* =========================================================================
       CODE VIEWER
       ========================================================================= */
    .stitch-code-box {
        background-color: #06090e;
        border: 1px solid var(--stitch-outline);
        border-radius: 4px;
        padding: 10px 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        line-height: 1.6;
        color: #e2e8f0;
        overflow-x: auto;
    }

    /* Streamlit Widget Overrides */
    div.stButton > button {
        background-color: var(--stitch-surface-high) !important;
        border: 1px solid var(--stitch-outline) !important;
        color: var(--stitch-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        border-radius: 3px !important;
        transition: all 0.15s ease !important;
    }

    div.stButton > button:hover {
        border-color: var(--stitch-primary-container) !important;
        background-color: var(--stitch-surface-highest) !important;
        color: #ffffff !important;
    }

    div.stButton > button[kind="primary"] {
        background-color: var(--stitch-primary-container) !important;
        color: var(--stitch-on-primary-container) !important;
        border: 1px solid var(--stitch-primary) !important;
        font-weight: 700 !important;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: var(--stitch-primary) !important;
        color: #000000 !important;
    }

    div.stDownloadButton > button {
        background-color: var(--stitch-surface-high) !important;
        border: 1px solid var(--stitch-outline) !important;
        color: var(--stitch-text) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 11px !important;
        border-radius: 3px !important;
    }

    div.stDownloadButton > button:hover {
        border-color: var(--stitch-tertiary) !important;
        color: var(--stitch-tertiary) !important;
    }

    /* Input & Select fields */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: var(--stitch-surface-lowest) !important;
        border-color: var(--stitch-outline) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
        color: var(--stitch-text) !important;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: var(--stitch-text) !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.015em !important;
    }
</style>
"""
