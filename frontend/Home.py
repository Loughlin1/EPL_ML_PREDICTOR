"""
Home.py

This module contains the Streamlit application for displaying the home page of the EPL Match Result Model.
"""

import logging

import streamlit as st

from frontend.logging_config import setup_logging
from frontend.utils.st_helper import initialize_session_state, next_matchweek, previous_matchweek

# Logging
LOGGER_NAME = "streamlit_ui"
setup_logging(LOGGER_NAME)
logger = logging.getLogger(LOGGER_NAME)


# Set the page layout to wide
st.set_page_config(page_title="EPL Match Result Predictor", layout="wide")

# Initialize session state
initialize_session_state(logger)
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
