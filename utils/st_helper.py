"""
st_helper.py

This module contains the helper functions for  Streamlit application for displaying the home page of the EPL Match Result Model.
"""

__author__ = "Loughlin Davidson"
__version__ = "1.0.0"

import os
import sys
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import streamlit as st
from utils.Predictor import get_predictions
from utils.Driver import *
from utils.Scraper import scrape_fixtures, get_top_points


def initialize_session_state() -> None:
    """
    Initialize session state for matchweek number, fixtures, and points.
    """
    if "all_fixtures" not in st.session_state or "all_points" not in st.session_state or "all_predictions" not in st.session_state:
        all_fixtures = get_fixtures()
        st.session_state.all_fixtures = all_fixtures
        st.session_state.all_predictions = get_predictions(all_fixtures)
        st.session_state.all_points = get_points(st.session_state.all_predictions)

    if 'matchweek_no' not in st.session_state:
        fixtures, matchweek_no = get_this_week(st.session_state.all_fixtures)
        st.session_state.matchweek_no = matchweek_no
        st.session_state.fixtures = fixtures
        st.session_state.points = get_points(get_predictions(fixtures))
        st.session_state.styled_df = get_predictions(fixtures).style.apply(highlight_rows, axis=None)

    # if "global_top_points" not in st.session_state or "global_top_250_points":
    #     global_top_points, global_top_250_points = get_top_points()
    #     st.session_state.global_top_points = global_top_points
    #     st.session_state.global_top_250_points = global_top_250_points


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
    st.session_state.points = get_points(df)
    st.session_state.styled_df = df.style.apply(highlight_rows, axis=None)
