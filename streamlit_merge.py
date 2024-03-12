import streamlit as st
import requests

# Define the ngrok URL where the FastAPI server is exposed
NGROK_URL = "https://1bb6-103-137-153-241.ngrok-free.app/"  # Replace this with your ngrok URL


# Define FastAPI endpoint
ANALYZE_SENTIMENT_ENDPOINT = "/analyze_sentiment/"

# Streamlit UI
st.title("Restaurant Sentiment Analysis")

# Input field for restaurant name
restaurant_name = st.text_input("Enter Restaurant Name")

# Button to trigger sentiment analysis
if st.button("Analyze Sentiment"):
    # Make a request to the FastAPI endpoint with the provided restaurant name
    try:
        response = requests.get(NGROK_URL + ANALYZE_SENTIMENT_ENDPOINT, params={"restaurant_name": restaurant_name})
        if response.status_code == 200:
            sentiment_data = response.json()
            st.write(f"Sentiment Score for {sentiment_data['restaurant_name']}: {sentiment_data['sentiment_score']}")
        else:
            st.error(f"Failed to analyze sentiment: {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {e}")
