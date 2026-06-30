import streamlit as st
from backend.py import main()

st.title("Wanderwise")
st.header("your personal travel assistant")

destination = st.text_input("Destination")
budget = st.number_input("Budget (£)", min_value=0)
interests = st.text_input("Interests")

if st.button("Generate Itinerary"):
    itinerary = main(dates, budget ,interests, travel_style)


    st.write(itinerary)