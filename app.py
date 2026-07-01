import streamlit as st
from backend_script import get_required_text, get_valid_budget, generate_itinerary , main , weather


st.title("Welcome to Wanderwise")
st.markdown("Your personal travel assistant")

if st.button("Create an itinerary"):
    st.markdown(main())
    city = get_required_text("Enter a city name for weather information:")
    print(f"City entered: {city}")  # Debugging line to check the input
    weather_info = weather(city)
    st.metric("Temperature (°C)", weather_info["temperature"])
    st.metric("Precipitation (mm)",weather_info["precipitation"])