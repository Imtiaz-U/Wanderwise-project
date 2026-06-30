import streamlit as st
from backend_script import get_valid_budget, generate_itinerary , main


st.title("Welcome to Wanderwise")
st.markdown("Your personal travel assistant")

if st.button("Create an itinerary"):
    st.markdown(main())