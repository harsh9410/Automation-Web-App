import os
import pywhatkit
import pyautogui
import time
import streamlit as st
import datetime
from gtts import gTTS
import base64

def speak(text):
    tts = gTTS(text)
    tts.save("speak.mp3")
    with open("speak.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        audio_html = f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

def extract_number(text):
    words_to_digits = {
        "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7,
        "eight": 8, "nine": 9, "ten": 10
    }
    if text.isdigit():
        return int(text)
    return words_to_digits.get(text.lower(), 1)

st.set_page_config(page_title="Automation App", page_icon="🤖")

st.title(" Automation Web App")
st.markdown("Choose an action: Date, Calendar or WhatsApp")

choice = st.selectbox("What do you want to do?", ["--Select--", "Date", "Calendar", "WhatsApp"])

if choice == "Date":
    current_date = datetime.date.today()
    st.success(f" Today's Date: {current_date}")
    speak(f"Today's date is {current_date}")

elif choice == "Calendar":
    try:
        output = os.popen("cal").read()
        st.text(f" Calendar:\n{output}")
        speak("Showing calendar")
    except Exception as e:
        st.error("Could not display calendar.")
        st.text(str(e))

elif choice == "WhatsApp":
    st.info("📲 This will open WhatsApp Web and send your message")

    number = st.text_input("Enter mobile number with country code", value="+91")
    message = st.text_input("Enter the message to send")
    repeat_count_text = st.text_input("How many times should I send the message?", value="1")

    if st.button("Send WhatsApp Message"):
        if number and message:
            repeat_count = extract_number(repeat_count_text)
            if not repeat_count:
                repeat_count = 1

            try:
                speak("Opening WhatsApp Web")
                st.success("Opening WhatsApp Web...")
                pywhatkit.sendwhatmsg_instantly(number, "Hi", wait_time=10, tab_close=False)
                speak("WhatsApp Web opened. Sending your message now")

                time.sleep(15)

                for i in range(repeat_count):
                    pyautogui.write(message)
                    pyautogui.press("enter")
                    time.sleep(0.5)

                st.success(f" Message sent {repeat_count} times successfully!")
                speak(f"Message sent {repeat_count} times")
            except Exception as e:
                st.error(f" Failed to send WhatsApp messages: {e}")
                speak("Failed to send message")
        else:
            st.warning("Please enter both number and message.")
