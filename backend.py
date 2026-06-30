##libraries
import os
from dotenv import load_dotenv
import sys
from groq import Groq

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
def main():
    print("======================================")
    print("        Welcome to Wanderwise         ")
    print("======================================")
    
    # Ask the user where they want to go and save their answer
    destination = input("\nWhere would you like to travel to? ")
    
    # Get the rest of the details needed for the brief
    dates = input("When are you going and for how long? ")
    budget = float(input("What is your total budget? £"))
    interests = input("What kind of things are you interested in? ")
    travel_style = input("What is your travel style? (e.g. budget, luxury, adventure) ")



    # Print a friendly message using the destination they just typed
    print(f"\nHello! Get ready to explore {destination}.")
    print("Your AI-powered itinerary is being prepared...\n")

    # This makes the call to the AI with our variables. This sends our prompt over the network.
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful travel assistant. Make a short, bullet-point itinerary."
            },
            {
                "role": "user",
                "content": f"Make a trip to {destination} for {dates}. My budget is £{budget} and I like {interests}, and my travel style is {travel_style}."
            }
        ],
        model="llama-3.3-70b-versatile",
        max_tokens=1000 # I put a hard limit here to make sure we stay within our token limit
    )

    print("\n=== Here is your itinerary ===")
    print(response.choices[0].message.content)
    print("\n==============================")


# This checks if we are running this exact file, rather than importing it somewhere else. If so, it starts the app.
if __name__ == "__main__":
    main()