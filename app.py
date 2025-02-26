import streamlit as st
from pint import UnitRegistry
import datetime
import pandas as pd
import random

# Initialize unit registry
ureg = UnitRegistry()

def convert_units(value, from_unit, to_unit):
    try:
        result = (value * ureg(from_unit)).to(to_unit)
        return result.magnitude, result.units
    except Exception as e:
        return None, str(e)

def log_conversion(value, from_unit, to_unit, result):
    with open("conversion_log.txt", "a") as log_file:
        log_file.write(f"{datetime.datetime.now()} - {value} {from_unit} -> {result} {to_unit}\n")

def load_conversion_history():
    try:
        with open("conversion_log.txt", "r") as log_file:
            lines = log_file.readlines()
        history_data = [line.strip().split(" - ") for line in lines]
        return pd.DataFrame(history_data, columns=["Timestamp", "Conversion"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Timestamp", "Conversion"])

def ai_suggestions(conversion_text):
    insights = [
        "Did you know? The metric system is used by 95% of the world!",
        "Fun Fact: A mile was originally defined as 1,000 Roman paces.",
        "Energy Tip: 1 kilowatt-hour can power a TV for about 10 hours!",
        "Speed Trivia: The fastest recorded human speed is 44.72 km/h!",
        "Water Insight: 1 liter of water weighs exactly 1 kilogram!"
    ]
    return random.choice(insights)

# Streamlit UI
st.set_page_config(page_title="🔄 Smart Unit Converter", page_icon="⚡", layout="centered")
st.title("⚡ Smart Unit Converter with AI Insights")
st.markdown("Convert units with ease and learn something new! 🚀")

# Sidebar for category selection
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

# Input fields
value = st.number_input("🔢 Enter Value", min_value=0.0, format="%.2f")
from_unit = st.selectbox("📍 From Unit", unit_options[category])
to_unit = st.selectbox("🎯 To Unit", unit_options[category])

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
                st.info(f"💡 AI Insight: {ai_suggestions(f'{value} {from_unit} to {converted_value:.2f} {unit}')} ")
            else:
                st.error("❌ Invalid Conversion!")

# Display conversion history
if st.sidebar.button("📜 Show Conversion History"):
    history_df = load_conversion_history()
    if not history_df.empty:
        with st.expander("🔍 View Conversion History"):
            st.dataframe(history_df, height=300)
            st.download_button("📥 Download History", history_df.to_csv(index=False), "conversion_history.csv")
    else:
        st.sidebar.error("⚠️ No history found!")

# Clear history button
if st.sidebar.button("🗑️ Clear History"):
    open("conversion_log.txt", "w").close()
    st.sidebar.success("✅ History cleared!")
