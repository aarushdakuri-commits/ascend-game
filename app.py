import streamlit as st
import pandas as pd
from google import genai
import plotly.express as px
import math

# 1. SETUP
API_KEY = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="ASCEND: Federal Command", layout="wide")

# 2. STATE MANAGEMENT
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "Capital": 5, "Wood": 3, "Steel": 0, "Concrete": 2,
        "Silicon": 0, "Energy": 0, "Water": 0, "Labor": 1
    }
if 'stats' not in st.session_state:
    st.session_state.stats = {"Economy": 20, "Living": 20, "Pressure": 1}
if 'history' not in st.session_state:
    st.session_state.history = []
if 'pass_go_count' not in st.session_state:
    st.session_state.pass_go_count = 0

# 3. SIDEBAR
st.sidebar.title("🎮 City Vitals")
st.session_state.stats["Economy"] = st.sidebar.slider("Economy ($)", 0, 100, st.session_state.stats["Economy"])
st.session_state.stats["Living"] = st.sidebar.slider("Living (♥)", 0, 100, st.session_state.stats["Living"])
st.session_state.stats["Pressure"] = st.sidebar.slider("Federal Pressure (⚠️)", 1, 20, st.session_state.stats["Pressure"])

st.sidebar.divider()
st.sidebar.subheader("📦 Inventory")
for mat, count in st.session_state.inventory.items():
    st.session_state.inventory[mat] = st.sidebar.number_input(f"{mat}", 0, 100, count)

# 4. MAIN DASHBOARD
st.title("🏙️ ASCEND: Digital Command Center")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🤖 Federal AI Auditor")
    scenario_input = st.text_area("Describe your turn...", placeholder="e.g. Spent 2 Concrete to build a Dam.")

    if st.button("Run Audit"):
        try:
            prompt = f"""
            Audit this city move: {scenario_input}.
            Stats: Econ {st.session_state.stats['Economy']}, Life {st.session_state.stats['Living']}, Pressure {st.session_state.stats['Pressure']}.
            Inventory: {st.session_state.inventory}.
            1. Grade this move (A-F).
            2. Predict how this affects the city long-term.
            """
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            st.success("Audit Received")
            st.write(response.text)

            st.session_state.history.append({
                "Turn": len(st.session_state.history) + 1,
                "Econ": st.session_state.stats["Economy"],
                "Life": st.session_state.stats["Living"]
            })
        except Exception as e:
            st.error(f"AI Offline. Error details: {e}")

    st.divider()

    # PASS GO BUTTON
    col_go1, col_go2 = st.columns([1, 2])
    with col_go1:
        if st.button("✅ Pass Go"):
            st.session_state.pass_go_count += 1
            st.success(f"Passed Go! ({st.session_state.pass_go_count}/6)")
    with col_go2:
        st.progress(st.session_state.pass_go_count / 6)
        st.caption(f"{st.session_state.pass_go_count}/6 laps completed")

    st.divider()
    df = pd.DataFrame(st.session_state.history)
    if not df.empty and "Turn" in df.columns:
        fig = px.line(df, x="Turn", y=["Econ", "Life"], title="City Growth Trajectory", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📊 Run your first audit to generate the growth chart.")

# 5. RANKING ENGINE
with col2:
    st.subheader("🇺🇸 National Ranking")

    target_e, target_l = 60, 55
    current_e = st.session_state.stats["Economy"]
    current_l = st.session_state.stats["Living"]

    dist = math.sqrt((target_e - current_e)**2 + (target_l - current_l)**2)

    st.metric("Distance to Ohio", f"{dist:.1f} pts")

    if dist < 5:
        st.success("You are essentially running Ohio right now.")
    else:
        st.write(f"Keep building. You need to close a gap of {dist:.1f} points to match Ohio's metrics.")

    st.divider()

    game_over = st.session_state.pass_go_count >= 6

    if game_over:
        if current_e >= 95 and current_l >= 90:
            st.balloons()
            st.success("🏆 METROPLEX STATUS ACHIEVED!")
            st.markdown("### Your city ranks among the greatest in America:")

            cities = [
                {"City": "New York, NY",      "Econ": 99, "Living": 97},
                {"City": "San Francisco, CA",  "Econ": 98, "Living": 94},
                {"City": "Seattle, WA",        "Econ": 97, "Living": 95},
                {"City": "Boston, MA",         "Econ": 96, "Living": 93},
                {"City": "Austin, TX",         "Econ": 95, "Living": 92},
                {"City": "Denver, CO",         "Econ": 94, "Living": 91},
                {"City": "Chicago, IL",        "Econ": 93, "Living": 90},
                {"City": "Nashville, TN",      "Econ": 92, "Living": 89},
                {"City": "Portland, OR",       "Econ": 91, "Living": 88},
                {"City": "Miami, FL",          "Econ": 90, "Living": 87},
                {"City": "Minneapolis, MN",    "Econ": 89, "Living": 86},
                {"City": "Atlanta, GA",        "Econ": 88, "Living": 85},
                {"City": "Dallas, TX",         "Econ": 87, "Living": 84},
                {"City": "Phoenix, AZ",        "Econ": 86, "Living": 83},
                {"City": "San Diego, CA",      "Econ": 85, "Living": 82},
                {"City": "Charlotte, NC",      "Econ": 84, "Living": 81},
                {"City": "Columbus, OH",       "Econ": 83, "Living": 80},
                {"City": "Indianapolis, IN",   "Econ": 82, "Living": 79},
                {"City": "Las Vegas, NV",      "Econ": 81, "Living": 78},
                {"City": "YOUR CITY 🏙️",      "Econ": current_e, "Living": current_l},
            ]

            cities_sorted = sorted(cities, key=lambda x: x["Econ"] + x["Living"], reverse=True)
            for i, city in enumerate(cities_sorted):
                city["Rank"] = i + 1

            df_cities = pd.DataFrame(cities_sorted)[["Rank", "City", "Econ", "Living"]]

            def highlight_player(row):
                if "YOUR CITY" in row["City"]:
                    return ["background-color: #ffd700; color: black"] * len(row)
                return [""] * len(row)

            st.dataframe(
                df_cities.style.apply(highlight_player, axis=1),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.error("❌ Game Over — Metroplex Status not reached.")
            st.write(f"You finished with **{current_e} Econ** and **{current_l} Living**.")
            st.write("You needed 95 Econ and 90 Living. Better luck next time!")
    else:
        st.info(f"🎮 Game ends after 6 laps. You're on lap {st.session_state.pass_go_count}.")
        st.markdown("**Win Condition:** Reach 95 Econ / 90 Living by lap 6.")