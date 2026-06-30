# WanderWise

An AI-powered travel assistant that generates personalised travel itineraries.

## Current Features

- Collects the user's destination, travel dates, budget, interests and travel style.
- Generates an itinerary using the Groq API.
- Loads the API key securely from a `.env` file.
- Detects when the API key is missing.

## Planned Features

- Streamlit graphical interface.
- Weather integration.
- Improved error handling.
- Unit tests.

## Technologies

- Python
- Groq API
- python-dotenv

## Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file containing:

```text
GROQ_API_KEY=your_api_key_here
```

Run the application:

```bash
python main.py
```