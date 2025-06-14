"""
Home.py

This module contains the Streamlit application for displaying the home page of the EPL Match Result Model.
"""

import streamlit as st
import pandas as pd
import schedule
import time

from backend.utils.predictions import get_predictions
from backend.utils.fixtures import get_fixtures, get_weeks_fixtures, get_this_week, highlight_rows
from backend.utils.superbru_points_calculator import get_superbru_points
from backend.utils.scraper import scrape_fixtures, get_top_points


def initialize_session_state() -> None:
    """
    Initialize session state for matchweek number, fixtures, and points.
    """
    if "all_fixtures" not in st.session_state or "all_points" not in st.session_state or "all_predictions" not in st.session_state:
        all_fixtures = get_fixtures()
        st.session_state.all_fixtures = all_fixtures
        st.session_state.all_predictions = get_predictions(all_fixtures)
        st.session_state.all_points = get_superbru_points(st.session_state.all_predictions)

    if 'matchweek_no' not in st.session_state:
        fixtures, matchweek_no = get_this_week(st.session_state.all_fixtures)
        st.session_state.matchweek_no = matchweek_no
        st.session_state.fixtures = fixtures
        st.session_state.points = get_superbru_points(get_predictions(fixtures))
        st.session_state.styled_df = get_predictions(fixtures).style.apply(highlight_rows, axis=None)

    # if "global_top_points" not in st.session_state or "global_top_250_points":
    #     global_top_points, global_top_250_points = get_top_points()
    #     st.session_state.global_top_points = global_top_points
    #     st.session_state.global_top_250_points = global_top_250_points

# Initialize session state
initialize_session_state()


def previous_matchweek() -> None:
    """
    Callback function for "Last Matchweek" button.
    Decrements the matchweek number and updates fixtures and points.
    """
    if st.session_state.matchweek_no > 1:
        st.session_state.matchweek_no -= 1
        update_fixtures_and_points()


def next_matchweek() -> None:
    """
    Callback function for "Next Matchweek" button.
    Increments the matchweek number and updates fixtures and points.
    """
    st.session_state.matchweek_no += 1
    update_fixtures_and_points()


def update_fixtures_and_points() -> None:
    """
    Update fixtures and points based on the current matchweek.
    """
    df = get_weeks_fixtures(st.session_state.all_predictions, st.session_state.matchweek_no)
    st.session_state.fixtures = df
    st.session_state.points = get_superbru_points(df)
    st.session_state.styled_df = df.style.apply(highlight_rows, axis=None)


# Title and Description
st.title('⚽️ EPL Match Result Predictor')
st.markdown('This is a web app to visualise match result predictions and calculate how many points it would score based on Superbru app')

# Display header for the selected matchweek
st.subheader(f"Matchweek {int(st.session_state.matchweek_no)} Results")

# Display points and the styled dataframe
columns = ['Day', 'Date', 'Time', 'Home', 'Score', 'Result', 'PredScore', 'PredResult', 'Away', 'Venue']
st.write(f'Superbru points this week: {st.session_state.points}')
st.write(f'Superbru points all weeks so far: {st.session_state.all_points}')
# st.write(f'Global Top is {st.session_state.global_top_points} points')
# st.write(f'Global 250th is {st.session_state.global_top_250_points} points')

st.dataframe(st.session_state.styled_df, hide_index=True, column_order=columns)

col1, col2, col3 = st.columns(3)

with col1:
    st.button("⏪ Last Matchweek", on_click=previous_matchweek)

with col2:
    st.button('Next Matchweek ⏩', on_click=next_matchweek)

with col3:
    st.button('Refresh Data 🔄', on_click=scrape_fixtures)

# # Schedule to fetch new data every hour
# schedule.every().hour.do(scrape_fixtures)

# while True:
#     schedule.run_pending()
#     time.sleep(1)