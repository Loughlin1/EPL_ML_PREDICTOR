import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.title("EPL Predictor")

st.write("Fetching prediction from the backend...")
response = requests.get(f"{API_URL}/predict")
if response.status_code == 200:
    prediction = response.json().get("prediction", "No prediction available")
    st.write(f"Prediction: {prediction}")
else:
    st.error("Failed to fetch prediction from the backend.")
