import os
import requests
import streamlit as st
import cohere
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
weather_api_key = os.getenv("WEATHER_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")

# Set up Cohere client
co = cohere.Client(cohere_api_key)

# Streamlit UI
st.set_page_config(page_title="Weather Outfit Advisor", page_icon="🌤️", layout="centered")
st.title("🌤️ Weather-Based Outfit Advisor")
# city = st.text_input("City:")

st.markdown('<label style="font-weight:700; font-size:18px;">City:</label>', unsafe_allow_html=True)
city = st.text_input("", placeholder="Enter city name", label_visibility="collapsed")

# Sidebar for extra options
with st.sidebar:
    st.header("Settings")
    units = st.radio("Units", ["Metric (°C)", "Imperial (°F)"], index=0)
    st.write("Powered by OpenWeatherMap & Cohere")

if city:
    try:
        # Get weather data
        unit_param = "metric" if units.startswith("Metric") else "imperial"
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units={unit_param}&appid={weather_api_key}"
        with st.spinner("Fetching weather data..."):
            response = requests.get(weather_url)
            data = response.json()

        if data.get("cod") != 200:
            st.error(f"City not found: {data.get('message', 'Unknown error')}")
        else:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            wind_speed = data['wind']['speed']
            humidity = data['main']['humidity']
            icon_code = data['weather'][0]['icon']
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

            # Weather summary
            st.image(icon_url, width=80)
            st.metric("Temperature", f"{temperature}°{'C' if unit_param=='metric' else 'F'}")
            st.metric("Humidity", f"{humidity}%")
            st.metric("Wind Speed", f"{wind_speed} {'m/s' if unit_param=='metric' else 'mph'}")
            st.info(f"**Weather:** {description.capitalize()}")


            # Prepare prompt
            weather_string = f"The temperature is {temperature}°C, it is {description}, with a wind speed of {wind_speed}m/s."
            prompt = f"""Based on the following weather, suggest an appropriate outdoor outfit.
            Break it down into:
            - 👕 Top
            - 👖 Bottom
            - 👟 Footwear
            - 🧢 Accessories
            
            Forecast: {weather_string}"""

            # Get LLM suggestion
            with st.spinner("Generating outfit suggestion..."):
                llm_response = co.chat(message=prompt)
                st.success("Here's your outfit suggestion:")
                st.markdown(llm_response.text)

    except Exception as e:
        st.error(f"Error occurred: {str(e)}")