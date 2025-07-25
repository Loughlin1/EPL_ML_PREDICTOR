"""
Home.py

This module contains the Streamlit application for displaying the home page of the EPL Match Result Model.
"""

import logging
import streamlit as st
import requests
import pandas as pd

from logging_config import setup_logging

API_BASE_URL = "http://localhost:8000/api"

# Logging
LOGGER_NAME = "streamlit_ui"
setup_logging(LOGGER_NAME)
logger = logging.getLogger(LOGGER_NAME)

st.set_page_config(page_title="EPL Match Result Predictor", layout="wide")


# ---------- Session Initialization ----------

def initialize_session_state():
    if "matchweek_no" not in st.session_state:
        # Fetch default matchweek from API
        response = requests.get(f"{API_BASE_URL}/matchweek")
        if response.status_code == 200:
            st.session_state.matchweek_no = response.json().get("current_matchweek", 1)
        else:
            st.session_state.matchweek_no = 1

    if "all_fixtures" not in st.session_state or "all_predictions" not in st.session_state or "all_points" not in st.session_state:
        fixtures_res = requests.get(f"{API_BASE_URL}/fixtures")
        preds_res = requests.post(f"{API_BASE_URL}/predict", json={"data": fixtures_res.json()})

        if fixtures_res.status_code == 200 and preds_res.status_code == 200:
            st.session_state.all_fixtures = pd.DataFrame(fixtures_res.json())
            st.session_state.all_predictions = pd.DataFrame(preds_res.json())
            points_res = requests.post(f"{API_BASE_URL}/superbru/points", json={"data": st.session_state.all_predictions.to_dict(orient="records")})
            st.session_state.all_points = points_res.json().get("points", 0) if points_res.status_code == 200 else 0

        else:
            st.error("Failed to fetch fixtures or predictions.")
            return

    update_fixtures_and_points()

def update_fixtures_and_points():
    mw = st.session_state.matchweek_no
    df = st.session_state.all_predictions
    df = df[df["Wk"] == mw]

    # Call Superbru scoring API
    points_res = requests.post(f"{API_BASE_URL}/superbru/points", json={"data": df.to_dict(orient="records")})
    points = points_res.json().get("points", 0) if points_res.status_code == 200 else 0

    st.session_state.points = points
    st.session_state.styled_df = df.style.apply(highlight_rows, axis=1)

# ---------- Changing matchweek/page ------------------

def previous_matchweek() -> None:
    """
    Callback function for "Last Matchweek" button.
    Decrements the matchweek number and updates fixtures and points.
    """
    st.session_state.matchweek_no -= 1
    update_fixtures_and_points()


def next_matchweek() -> None:
    """
    Callback function for "Next Matchweek" button.
    Increments the matchweek number and updates fixtures and points.
    """
    st.session_state.matchweek_no += 1
    update_fixtures_and_points()

# ---------- Row Highlighting ----------

def highlight_rows(row):
    if row["Score"] and row["PredScore"] == row["Score"]:
        return ['background-color: #3CB371'] * len(row)
    if row["Score"] and row["PredResult"] == row["Result"]:
        return ['background-color: #FFDB58'] * len(row)
    else:
        return [''] * len(row)

# ---------- UI Rendering ----------

initialize_session_state()
# Title and Description
st.title("⚽️ EPL Match Result Predictor")
st.markdown("This is a web app to visualise match result predictions and calculate how many points it would score based on Superbru app")

# Display header for the selected matchweek
st.subheader(f"Matchweek {int(st.session_state.matchweek_no)} Results")

# Display points and the styled dataframe
columns = [
    "Day",
    "Date",
    "Time",
    "HomeTeam",
    "Score",
    "Result",
    "PredScore",
    "PredResult",
    "AwayTeam",
    "Venue",
]
st.write(f"Superbru points this week: {st.session_state.points}")
st.write(f"Superbru points all weeks so far: {st.session_state.all_points}")
# st.write(f'Global Top is {st.session_state.global_top_points} points')
# st.write(f'Global 250th is {st.session_state.global_top_250_points} points')

st.dataframe(
    st.session_state.styled_df, hide_index=True, column_order=columns, column_config={"Date": st.column_config.DatetimeColumn(format="DD/MM/YYYY")}
)

col1, col2 = st.columns(2)

with col1:
    if st.session_state.matchweek_no > 1:
        st.button("⏪ Last Matchweek", on_click=previous_matchweek)

with col2:
    if st.session_state.matchweek_no < 38:
        st.button("Next Matchweek ⏩", on_click=next_matchweek)


# # Schedule to fetch new data every hour
# schedule.every().hour.do(scrape_fixtures)

# while True:
#     schedule.run_pending()
#     time.sleep(1)
