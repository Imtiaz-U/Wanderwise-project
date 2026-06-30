import streamlit as st

st.title("Welcome to Wanderwise")
st.markdown("Your personal travel assistant")

if st.button("Create an itinerary"):
    st.markdown(main())