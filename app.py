import streamlit as st
from datetime import date, timedelta

# weather aliased so it doesn't clash with the weather_info variable below
from backend_script import generate_itinerary, weather as get_weather, transcribe_audio

# ---- page config ----
st.set_page_config(page_title="Wanderwise", page_icon="🧭", layout="wide")

# ---- styling ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --cream:      #F7F1E3;
    --navy:       #1B3358;
    --mustard:    #D98E04;
    --terracotta: #C1502E;
    --ink:        #2B2620;
}

.stApp { background-color: var(--cream); }

h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: var(--navy) !important; }
p, label, .stMarkdown, div[data-testid="stWidgetLabel"] p {
    font-family: 'Inter', sans-serif !important; color: var(--ink) !important;
}

.ww-hero {
    border-bottom: 3px solid var(--navy);
    padding-bottom: 1.2rem;
    margin-bottom: 1.8rem;
}
.ww-eyebrow {
    font-family: 'Inter', sans-serif;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--terracotta);
}

/* boarding pass card */
.ww-ticket {
    background: white;
    border: 2px solid var(--navy);
    border-radius: 4px;
    padding: 1.75rem;
    position: relative;
    margin-top: 1rem;
}
.ww-ticket::before {
    content: "";
    position: absolute;
    top: -10px; left: 24px; right: 24px;
    border-top: 2px dashed var(--mustard);
}
.ww-ticket-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 1px dashed var(--navy);
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
}
.ww-ticket-route { font-family: 'Playfair Display', serif; font-size: 1.4rem; color: var(--navy); }
.ww-ticket-stub  { font-family: 'Inter', sans-serif; font-size: 0.7rem; letter-spacing: 0.1em;
                   text-transform: uppercase; color: var(--mustard); font-weight: 600; }

/* weather card */
.ww-weather {
    background: var(--navy);
    border-radius: 4px;
    padding: 1.5rem;
    text-align: center;
    margin-top: 1rem;
}
.ww-weather h3        { color: var(--cream) !important; margin-bottom: 0.25rem; }
.ww-weather-temp      { font-family: 'Playfair Display', serif; font-size: 2.6rem; color: var(--mustard) !important; }
.ww-weather-desc      { font-family: 'Inter', sans-serif; color: var(--cream) !important; opacity: 0.85; }

/* voice section */
.ww-voice-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--terracotta);
    margin-bottom: 0.4rem;
}

.stButton button {
    background-color: var(--terracotta) !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.8rem !important;
    letter-spacing: 0.03em;
}
.stButton button:hover { background-color: var(--navy) !important; }
</style>
""", unsafe_allow_html=True)

# ---- hero ----
st.markdown("""
<div class="ww-hero">
    <div class="ww-eyebrow">Your trip, planned in seconds</div>
    <h1>Wanderwise ✈</h1>
    <p>Tell us where you're headed — we'll hand you back a ready-made itinerary.</p>
</div>
""", unsafe_allow_html=True)

# ---- voice input (optional — transcribes into the destination field below) ----
st.markdown('<div class="ww-voice-label">🎙 Speak your destination (optional)</div>', unsafe_allow_html=True)
audio_recording = st.audio_input("Record your destination")

# transcribe as soon as they stop recording — result pre-fills the text box below
voice_destination = ""
if audio_recording is not None:
    with st.spinner("Transcribing..."):
        voice_destination = transcribe_audio(audio_recording.read())
    if voice_destination:
        st.success(f'Heard: "{voice_destination}"')
    else:
        st.warning("Couldn't make that out — just type it in below.")

st.divider()

# ---- inputs ----
left_col, right_col = st.columns(2)

with left_col:
    # pre-fill with the voice result if we got one, otherwise leave blank
    destination = st.text_input(
        "Where would you like to travel to?",
        value=voice_destination,
        placeholder="e.g. Lisbon, Portugal",
    )
    trip_dates = st.date_input(
        "When are you going?",
        value=(date.today() + timedelta(days=30), date.today() + timedelta(days=37)),
    )

with right_col:
    budget = st.slider("What is your total budget? (£)", min_value=100, max_value=10000, value=1500, step=50)
    travel_style = st.selectbox(
        "What is your travel style?",
        ["Budget", "Mid-range", "Luxury", "Adventure", "Relaxed"],
    )

interests = st.multiselect(
    "What kind of things are you interested in?",
    ["Food & drink", "History & culture", "Nature & outdoors", "Nightlife",
     "Art & museums", "Shopping", "Relaxation", "Architecture"],
)

create_clicked = st.button("Create my itinerary")

# ---- output ----
if create_clicked:
    # same empty-field checks as get_required_text() in the backend
    if not destination.strip():
        st.error("Please tell us where you'd like to travel to.")
    elif not interests:
        st.error("Pick at least one interest so we know what to plan around.")
    elif len(trip_dates) != 2:
        st.error("Please select both a start and end date.")
    else:
        start_date, end_date = trip_dates
        dates_text     = f"{start_date.strftime('%d %b %Y')} to {end_date.strftime('%d %b %Y')}"
        interests_text = ", ".join(interests)

        with st.spinner("Putting your itinerary together..."):
            itinerary    = generate_itinerary(destination, dates_text, budget, interests_text, travel_style)
            weather_info = get_weather(destination)

        result_col, weather_col = st.columns([2, 1])

        with result_col:
            st.markdown(f"""
            <div class="ww-ticket">
                <div class="ww-ticket-header">
                    <div class="ww-ticket-route">{destination}</div>
                    <div class="ww-ticket-stub">{dates_text}</div>
                </div>
                <div>{itinerary.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

        with weather_col:
            if "error" not in weather_info:
                st.markdown(f"""
                <div class="ww-weather">
                    <h3>Right now in {destination}</h3>
                    <div class="ww-weather-temp">{weather_info['temperature']}°C</div>
                    <div class="ww-weather-desc">Precipitation: {weather_info['precipitation']} mm</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # weather failing shouldn't kill the whole thing
                st.markdown("""
                <div class="ww-weather">
                    <h3>Weather</h3>
                    <div class="ww-weather-desc">Not available right now</div>
                </div>
                """, unsafe_allow_html=True)