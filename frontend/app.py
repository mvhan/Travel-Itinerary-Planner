# frontend/app.py
import streamlit as st
import requests

st.set_page_config(page_title="Travel Itinerary Planner", layout="wide")
st.title("🧳 Travel Itinerary Planner")

BASE_URL = "http://127.0.0.1:8000"

# ---- SESSION STATE ----
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None


# ---------- LOGIN / REGISTER ----------
if st.session_state.user_id is None:
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            res = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
            data = res.json()
            if res.status_code == 200:
                st.session_state.user_id = data["user_id"]
                st.session_state.username = username
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error(data.get("error", "Login failed."))

    with tab2:
        new_user = st.text_input("New username")
        new_pass = st.text_input("New password", type="password")
        if st.button("Register"):
            res = requests.post(f"{BASE_URL}/register", json={"username": new_user, "password": new_pass})
            data = res.json()
            if res.status_code == 201:
                st.success("Registration successful! You can now login.")
            else:
                st.error(data.get("error", "Registration failed."))
    st.stop()


# ---------- MAIN APP ----------
st.sidebar.success(f"👋 Logged in as {st.session_state.username}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.user_id = None
    st.session_state.username = None
    st.rerun()


with st.form("travel_form"):
    origin = st.text_input("From:", "Ha Noi")
    destination = st.text_input("To:", "Da Lat")
    start_date = st.date_input("Start date")
    end_date = st.date_input("End date")
    interests = st.multiselect("Traveler interests:", ["Food", "Museums", "Nature", "Nightlife"], ["Food"])
    pace = st.selectbox("Travel pace:", ["Relaxed", "Normal", "Tight"], index=1)
    submitted = st.form_submit_button("Generate Itinerary")

if submitted:
    st.info("🔄 Generating itinerary... Please wait...")
    payload = {
        "origin": origin,
        "destination": destination,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "interests": interests,
        "pace": pace,
        "user_id": st.session_state.user_id
    }

    try:
        response = requests.post(f"{BASE_URL}/generate", json=payload, timeout=300)
        itinerary = response.json()
        if response.status_code == 200 and "error" not in itinerary:
            st.success("✅ Suggested Itinerary:")
            for day, activities in itinerary.items():
                with st.expander(day, expanded=True):
                    for time_of_day in ["Morning", "Afternoon", "Evening"]:
                        st.markdown(f"**{time_of_day}:** {activities.get(time_of_day, '(No activity)')}")
        else:
            st.error(itinerary.get("error", "Something went wrong."))
            if "raw_output" in itinerary:
                st.code(itinerary["raw_output"])
    except requests.exceptions.Timeout:
        st.error("Backend timeout. Try shorter prompt or fewer days.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


# ---------- HISTORY ----------
st.markdown("---")
if st.button("📜 View My History"):
    res = requests.get(f"{BASE_URL}/history/{st.session_state.user_id}")
    if res.status_code == 200:
        history = res.json()
        if not history:
            st.info("No travel history yet.")
        else:
            for record in history:
                st.subheader(f"{record['origin']} ➜ {record['destination']} ({record['start_date']} → {record['end_date']})")
                st.caption(f"🕒 {record['timestamp']}")
                for day, activities in record["itinerary"].items():
                    with st.expander(day):
                        for time_of_day in ["Morning", "Afternoon", "Evening"]:
                            st.markdown(f"**{time_of_day}:** {activities.get(time_of_day, '(No activity)')}")
                st.markdown("---")
    else:
        st.error("Could not load history.")
