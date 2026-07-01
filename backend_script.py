##libraries
import os
from dotenv import load_dotenv
import sys
import requests
from groq import Groq
# Pulling in the specific error types Groq can throw, so we can react differently
# depending on what actually went wrong (rate limit vs. no internet vs. server is down, etc.)
from groq import APIConnectionError, APITimeoutError, RateLimitError, APIStatusError, GroqError

# Load our hidden secrets (like API keys, like abrar's secret keys) from the .env file so the code can use them safely
load_dotenv()

##variable##
api_key = os.getenv("GROQ_API_KEY")

#handle a missing API key 
if not api_key:
    print("\nError: We could not find your GROQ_API_KEY.")
    print("Please ensure you have a .env file in your project folder that contains: GROQ_API_KEY=your_actual_key_here\n")
    sys.exit()

client = Groq(api_key=api_key)



##subprograms

def get_valid_budget():
    # Keep asking the user until they give us a proper number
    budget_is_valid = False
    
    while budget_is_valid == False:
        user_input = input("What is your total budget? £")
        
        try:
            # Try to turn their answer into a decimal number
            budget = float(user_input)
            
            # Check if it is a negative number or zero
            if budget <= 0:
                print("Please enter a budget greater than zero.")
            else:
                budget_is_valid = True
                return budget
                
        except ValueError:
            # If the float conversion breaks (for example, they typed 'five'), this catches the error
            print("Invalid input. Please type a number like 500 or 1250.50")


def get_required_text(prompt_message):
    # We  need SOMETHING here - we can't send an empty string off to the AI and expect a trip back.
    while True:
        user_input = input(prompt_message).strip()

        if user_input == "":
            # We're using the function .strip() which means "   " (just spaces) and also counts as empty, not just ""
            print("This can't be left empty - please type an answer.")
        else:
            return user_input


def generate_itinerary(destination, dates, budget, interests, travel_style):
    # We put this in a try block just in case the internet drops or the AI crashes
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful travel assistant. Make a short, bullet-point itinerary."
                },
                {
                    "role": "user",
                    "content": f"Make a trip to {destination} for {dates}. My budget is £{budget}, I like {interests}, and my travel style is {travel_style}."
                }
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=1000 
        )

        # Sometimes an API can technically succeed but hand back something unexpected
        # (e.g. no choices at all) - better to check than to crash on response.choices[0]
        if not response.choices:
            return "Hmm, the AI didn't send back any suggestions that time. Please try again."

        # Give back the text the AI generated
        return response.choices[0].message.content

    # These errors are ordered from  most-specific to least-specific, since Python checks them top to bottom.
    except APITimeoutError:
        # The request took too long and gave up - usually a slow connection or a busy server
        return "Oops! The request to the AI timed out. Please check your connection and try again."

    except APIConnectionError:
        # We couldn't even reach Groq's servers - likely no internet 
        return "Oops! We couldn't connect to the AI. Please check your internet connection and try again."

    except RateLimitError:
        # We've sent too many requests too quickly
        return "Oops! We've hit the AI's rate limit. Please wait a moment and try again."

    except APIStatusError as error_message:
        # Groq's servers responded, but with an error status (e.g. bad request, server error)
        return f"Oops! The AI service returned an error (status {error_message.status_code}). Please try again later."

    except GroqError as error_message:
        # A catch-all for any other Groq-specific issue we haven't handled above
        return f"Oops! Something went wrong talking to the AI. Here is the error: {error_message}"

    except Exception as error_message:
        # If something goes wrong, tell the user instead of crashing the whole app
        return f"Oops! We had trouble connecting to the AI. Here is the error: {error_message}"

def main():
    print("======================================")
    print("        Welcome to Wanderwise         ")
    print("======================================")
    
    # Ask the user where they want to go and save their answer
    destination = get_required_text("\nWhere would you like to travel to? ")
    
    # Get the rest of the details needed for the brief
    dates = get_required_text("When are you going and for how long? ")

    # Use our robust function to get the budget safely
    budget = get_valid_budget()

    interests = get_required_text("What kind of things are you interested in? ")
    travel_style = get_required_text("What is your travel style? (e.g. budget, luxury, adventure) ")



    # Print a friendly message using the destination they just typed
    print(f"\nHello! Get ready to explore {destination}.")
    print("Your AI-powered itinerary is being prepared...\n")

     # This makes the call to the AI with our variables
    itinerary = generate_itinerary(destination, dates, budget, interests, travel_style)

    print("\n=== Here is your itinerary ===")
    print(itinerary)
    print("\n==============================")

def weather(city):
    print("weather function called")
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=en&format=json"
    
    geo_response = requests.get(geo_url)
    if geo_response.status_code != 200:
        return {"error": "Failed to fetch location data"}
    
    geo_data = geo_response.json()


    if "results" not in geo_data:
        return{"error": "location not found"}
    

    location = geo_data["results"][0]

    latitude = location["latitude"]
    longitude = location["longitude"]

    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,precipitation&forecast_days=7"

    weather_response = requests.get(weather_url)
    if weather_response.status_code != 200:
        return {"error": "Failed to fetch weather data"}
    
    current_weather = weather_response.json()
    return current_weather




# This checks if we are running this exact file, rather than importing it somewhere else. If so, it starts the app.
if __name__ == "__main__":
    main()