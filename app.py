from pathlib import Path
import streamlit as st

from pathlib import Path
import streamlit as st

from components.data_loader import load_csv_data

from components.pages import (
    overview,
    bengaluru_page,
    chennai_page,
    integration_page,
    quality_page
)

# =====================================
# 1. PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="AquaScope | Water Analytics",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =====================================
# 2. LOAD CSS
# =====================================

BASE = Path(__file__).resolve().parent
CSS_FILE = BASE / "assets" / "style.css"

if CSS_FILE.exists():
    st.html(
        f"<style>{CSS_FILE.read_text(encoding='utf-8')}</style>"
    )

# =====================================
# 3. INITIALIZE SESSION STATE
# =====================================

if "menu_open" not in st.session_state:
    st.session_state.menu_open = False

if "navigation" not in st.session_state:
    st.session_state.navigation = "🏠 Dashboard"

# =====================================
# 4. MENU TOGGLE
# =====================================

def toggle_menu():
    st.session_state.menu_open = (
        not st.session_state.menu_open
    )

st.button(
    "✕ Close Menu"
    if st.session_state.menu_open
    else "☰ Open Menu",
    key="custom_menu_button",
    on_click=toggle_menu
)

# =====================================
# 5. CUSTOM LEFT NAVIGATION
# =====================================

if st.session_state.menu_open:
    menu_col, content_col = st.columns(
        [1, 3.5],
        gap="large"
    )
else:
    content_col = st.container()

if st.session_state.menu_open:

    with menu_col:
        with st.container(border=True):

            st.markdown("## 💧 AquaScope")
            st.caption("WATER INTELLIGENCE PLATFORM")

            st.divider()

            st.markdown("### Explore Analytics")

            st.radio(
                "Navigation",
                [
                    "🏠 Dashboard",
                    "🏙️ Bengaluru Analytics",
                    "🌊 Chennai Analytics",
                    "🔗 Data Integration",
                    "🛡️ Data Quality"
                ],
                key="navigation",
                label_visibility="collapsed"
            )

            st.divider()

            st.caption("📍 Bengaluru, Karnataka")
            st.caption("📍 Chennai, Tamil Nadu")

            st.caption(
                "Python • Pandas • "
                "Matplotlib • Streamlit"
            )

# =====================================
# 6. LOAD DATA
# =====================================

page = st.session_state.navigation

try:
    with st.spinner("Loading CSV datasets..."):
        bengaluru, chennai, combined = (
            load_csv_data()
        )

except Exception as error:
    with content_col:
        st.error("Unable to load project data.")

        with st.expander("Show Error Details"):
            st.code(str(error))

    st.stop()

# =====================================
# 7. MAIN DASHBOARD CONTENT
# =====================================

with content_col:

    st.html("""
<div class="hero">
    <div class="eyebrow">
        WATER ANALYTICS PLATFORM
    </div>
    <h1>💧 AquaScope Analytics</h1>
    <p>
        Interactive Water Consumption Pattern Analyzer
        for Bengaluru and Chennai, India.
    </p>
</div>
""")

    # =================================
    # 8. PAGE NAVIGATION
    # =================================

    if page == "🏠 Dashboard":
        overview(bengaluru, chennai, combined)

    elif page == "🏙️ Bengaluru Analytics":
        bengaluru_page(bengaluru)

    elif page == "🌊 Chennai Analytics":
        chennai_page(chennai)

    elif page == "🔗 Data Integration":
        integration_page(combined)

    elif page == "🛡️ Data Quality":
        quality_page(bengaluru, chennai)