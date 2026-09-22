APP_CSS = """
<style>
    .stApp { background: #F4F6F9; }
    [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #DCE3EC; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 { color: #0019A8; }
    .block-container { max-width: 1480px; padding-top: 1.4rem; padding-bottom: 3rem; }
    h1 { color: #0019A8; font-size: 2.05rem !important; letter-spacing: -0.02em; }
    h2, h3 { color: #172033; }
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DCE3EC;
        border-top: 4px solid #0019A8;
        border-radius: 8px;
        padding: 0.9rem 1rem;
        min-height: 126px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    div[data-testid="stMetric"] label { color: #475569; font-weight: 700; }
    div[data-testid="stMetricValue"] { color: #172033; }
    .scope-note {
        background: #EEF3FF;
        border-left: 4px solid #0019A8;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        margin: 0.25rem 0 1.1rem 0;
        color: #263449;
    }
    .warning-note {
        background: #FFF7D6;
        border-left: 4px solid #F59E0B;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        margin: 0.25rem 0 1.1rem 0;
        color: #4B3A12;
    }
    .leader {
        background: #FFFFFF;
        border: 1px solid #DCE3EC;
        border-left: 5px solid #E32017;
        padding: 0.9rem 1rem;
        border-radius: 7px;
        margin-bottom: 1rem;
    }
    footer { visibility: hidden; }
</style>
"""

# Network signage is deliberately sharper and darker than the other project UIs.
APP_CSS += """
<style>
.stApp { background: #F1F4F8; border-top: 7px solid #0019A8; font-family: 'Trebuchet MS', Arial, sans-serif; }
[data-testid="stHeader"] { background: #F1F4F8; }
[data-testid="stSidebar"] { background: #14233D; border-right: 4px solid #E32017; }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] [role="radiogroup"] * { color: #F8FAFC !important; }
[data-testid="stSidebar"] h1, h1, h2, h3 { font-family: 'Arial Narrow', 'Trebuchet MS', Arial, sans-serif; }
[data-testid="stSidebar"] h1, h1 { text-transform: uppercase; letter-spacing: .04em; font-weight: 800 !important; }
[data-testid="stSidebar"] hr { border-color: #52627D; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background: #243757; border-color: #52627D; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: #FFFFFF; }
div[data-testid="stMetric"] { border-top: 5px solid #0019A8; border-radius: 2px; box-shadow: 0 2px 0 #D6E0E8; }
div[data-testid="stMetricValue"] { font-family: 'Arial Narrow', 'Trebuchet MS', Arial, sans-serif; }
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] { border-radius: 2px; border-color: #D6E0E8; padding: .45rem; }
.scope-note, .warning-note, .leader { border-radius: 2px; }
</style>
"""
