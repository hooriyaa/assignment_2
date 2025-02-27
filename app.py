import streamlit as st
from pint import UnitRegistry
import datetime
import pandas as pd
import google.generativeai as genai
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Get API Key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Initialize unit registry
ureg = UnitRegistry()

# Conversion function
def convert_units(value, from_unit, to_unit):
    try:
        result = (value * ureg(from_unit)).to(to_unit)
        return result.magnitude, result.units
    except Exception as e:
        return None, str(e)

# Log conversion history
def log_conversion(value, from_unit, to_unit, result):
    with open("conversion_log.txt", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - {value} {from_unit} -> {result} {to_unit}\n")

# Load conversion history
def load_conversion_history():
    try:
        with open("conversion_log.txt", "r") as log_file:
            lines = log_file.readlines()
        history_data = [line.strip().split(" - ") for line in lines]
        return pd.DataFrame(history_data, columns=["Timestamp", "Conversion"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamp", "Conversion"])

# Fun AI insights
def ai_suggestions():
    insights = [
        "Did you know? The metric system is used by 95% of the world!",
        "Fun Fact: A mile was originally defined as 1,000 Roman paces.",
        "Energy Tip: 1 kilowatt-hour can power a TV for about 10 hours!",
        "Speed Trivia: The fastest recorded human speed is 44.72 km/h!",
        "Water Insight: 1 liter of water weighs exactly 1 kilogram!"
    ]
    return random.choice(insights)

# Streamlit UI setup
st.set_page_config(page_title="🔄 Smart Unit Converter", page_icon="⚡", layout="centered")
st.title("⚡ Smart Unit Converter with AI Insights")
st.markdown("Convert units easily and learn something new! 🚀")

# Sidebar category selection
category = st.sidebar.selectbox("📌 Select Category", [
    "Length", "Weight", "Temperature", "Speed", "Time", "Volume", "Area", "Energy"
])

unit_options = {
    "Length": ["meter", "kilometer", "mile", "yard", "foot", "inch"],
    "Weight": ["gram", "kilogram", "pound", "ounce", "ton"],
    "Temperature": ["celsius", "fahrenheit", "kelvin"],
    "Speed": ["meter/second", "kilometer/hour", "mile/hour", "knot"],
    "Time": ["second", "minute", "hour", "day"],
    "Volume": ["liter", "milliliter", "gallon", "cubic meter", "cup"],
    "Area": ["square meter", "square kilometer", "square foot", "square inch", "acre", "hectare"],
    "Energy": ["joule", "kilojoule", "calorie", "kilocalorie", "watt hour", "kilowatt hour"]
}

# Input fields for conversion
value = st.number_input("🔢 Enter Value", min_value=0.0, format="%.2f")
from_unit = st.selectbox("📍 From Unit", unit_options[category])
to_unit = st.selectbox("🎯 To Unit", unit_options[category])

# Conversion logic
if st.button("🚀 Convert", use_container_width=True):
    if from_unit and to_unit:
        if category == "Temperature":
            try:
                conversions = {
                    ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
                    ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
                    ("celsius", "kelvin"): lambda x: x + 273.15,
                    ("kelvin", "celsius"): lambda x: x - 273.15,
                    ("fahrenheit", "kelvin"): lambda x: (x - 32) * 5/9 + 273.15,
                    ("kelvin", "fahrenheit"): lambda x: (x - 273.15) * 9/5 + 32
                }
                result = conversions.get((from_unit, to_unit), lambda x: x)(value)
                st.success(f"🎉 Converted Value: {result:.2f} {to_unit}")
                log_conversion(value, from_unit, to_unit, result)
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            converted_value, unit = convert_units(value, from_unit, to_unit)
            if converted_value is not None:
                st.success(f"🎉 Converted Value: {converted_value:.2f} {unit}")
                log_conversion(value, from_unit, to_unit, converted_value)
                st.info(f"💡 AI Insight: {ai_suggestions()} ")
            else:
                st.error("❌ Invalid Conversion!")

# Sidebar: Toggle conversion history
show_history = st.sidebar.checkbox("📜 Show History", key="show_history")

if show_history:
    st.sidebar.subheader("📜 Conversion History")
    st.session_state.quick_reply = None
    history_df = load_conversion_history()
    if not history_df.empty:
        st.sidebar.dataframe(history_df, height=250)
        st.sidebar.download_button("📥 Download History", history_df.to_csv(index=False), "conversion_history.csv")
    else:
        st.sidebar.write("⚠️ No history found!")

# Clear history button
if st.sidebar.button("🗑️ Clear History"):
    open("conversion_log.txt", "w").close()
    st.sidebar.success("✅ History cleared!")

# AI Chatbot Section
st.header("🤖 Smart Gemini AI Chatbot")
st.write("Ask me anything!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

quick_replies = ["What can you do?", "Tell me a fun fact!", "How does unit conversion work?", "What's the latest tech trend?"]
selected_reply = st.sidebar.radio("💡 Quick Questions", quick_replies, index=None, key="quick_reply")

user_input = st.chat_input("Type your message...")
final_input = user_input if user_input else selected_reply

if final_input:
    st.session_state.messages.append({"role": "user", "content": final_input})
    with st.chat_message("user"):
        st.markdown(final_input)

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            try:
                model = genai.GenerativeModel("gemini-1.5-pro")
                prompt = f"""
                You are a helpful AI assistant. Answer all types of questions accurately.

                If the user asks anything related to 'who created you', 'who made you', or 'who is your developer', 
                respond with: 'I was created by **Hooriya Muhammad Fareed**. She is a passionate web developer with expertise in **HTML, CSS, JavaScript, React.js, Next.js, and TypeScript**.'

                User: {final_input}
                """
                response = model.generate_content(prompt)
                ai_reply = response.text
            except Exception as e:
                ai_reply = f"⚠️ Error: {str(e)}"

        st.markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

st.markdown("---")
st.markdown("❤️ Created by Hooriya Muhammad Fareed ❤️")
