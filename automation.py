import os
import time
import datetime
import base64
import subprocess
import requests
import pyperclip
import streamlit as st
import pyautogui
import pywhatkit
from gtts import gTTS
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------ TEXT TO SPEECH ------------------
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
    os.remove("speak.mp3")

# ------------------ TEXT TO NUMBER ------------------
def extract_number(text):
    words_to_digits = {
        "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7,
        "eight": 8, "nine": 9, "ten": 10
    }
    if text.isdigit():
        return int(text)
    return words_to_digits.get(text.lower(), 1)

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Automation App", page_icon="🤖")
st.title("🤖 All-in-One Automation App")

choice = st.selectbox("Choose an action", [
    "--Select--", "WhatsApp", "Email", "SMS", "Phone Call", "Post Tweet", "LinkedIn Post"
])

# ------------------ WHATSAPP ------------------
if choice == "WhatsApp":
    st.info("📲 Send messages via WhatsApp Web")
    number = st.text_input("Phone Number with +91")
    message = st.text_input("Message")
    repeat_text = st.text_input("Repeat count (e.g. one, two)", value="1")

    if st.button("Send WhatsApp Message"):
        if number and message:
            repeat = extract_number(repeat_text)
            try:
                speak("Opening WhatsApp Web")
                pywhatkit.sendwhatmsg_instantly(number, "Hi", wait_time=15, tab_close=False)
                time.sleep(20)
                for _ in range(repeat):
                    pyautogui.write(message)
                    pyautogui.press("enter")
                    time.sleep(0.5)
                st.success(f"✅ Sent {repeat} times.")
                speak("Message sent successfully")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                speak("Failed to send WhatsApp message")
        else:
            st.warning("Please fill all fields.")

# ------------------ EMAIL ------------------
elif choice == "Email":
    st.info("📧 Send email using Gmail App Password")
    sender = st.text_input("Your Email")
    app_pass = st.text_input("App Password", type="password")
    recipient = st.text_input("Recipient Email")
    subject = st.text_input("Subject")
    body = st.text_area("Email Body")

    if st.button("Send Email"):
        if sender and app_pass and recipient:
            try:
                msg = MIMEMultipart()
                msg['From'] = sender
                msg['To'] = recipient
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender, app_pass)
                server.sendmail(sender, recipient, msg.as_string())
                server.quit()

                st.success("✅ Email sent successfully!")
                speak("Email sent")
            except Exception as e:
                st.error(f"❌ {e}")
                speak("Email sending failed")
        else:
            st.warning("Fill all required fields.")

# ------------------ SMS ------------------
elif choice == "SMS":
    st.info("📩 Send SMS via Twilio")
    sid = st.text_input("Twilio SID")
    token = st.text_input("Auth Token", type="password")
    from_num = st.text_input("Twilio Number")
    to_num = st.text_input("Recipient Number")
    msg = st.text_input("Message")

    if st.button("Send SMS"):
        if sid and token and from_num and to_num and msg:
            try:
                client = Client(sid, token)
                message = client.messages.create(body=msg, from_=from_num, to=to_num)
                st.success(f"✅ SMS sent! SID: {message.sid}")
                speak("SMS sent successfully")
            except Exception as e:
                st.error(f"❌ {e}")
                speak("SMS sending failed")
        else:
            st.warning("Please fill all fields.")

# ------------------ PHONE CALL ------------------
elif choice == "Phone Call":
    st.info("📞 Call using Twilio")
    sid = st.text_input("Twilio SID")
    token = st.text_input("Auth Token", type="password")
    from_num = st.text_input("Twilio Number")
    to_num = st.text_input("Recipient Number")
    twiml_url = st.text_input("TwiML Bin URL")

    if st.button("Make Call"):
        if sid and token and from_num and to_num and twiml_url:
            try:
                client = Client(sid, token)
                call = client.calls.create(to=to_num, from_=from_num, url=twiml_url)
                st.success(f"📞 Call initiated! SID: {call.sid}")
                speak("Call made successfully")
            except Exception as e:
                st.error(f"❌ {e}")
                speak("Call failed")
        else:
            st.warning("Fill all fields.")

# ------------------ TWEET POST ------------------
elif choice == "Post Tweet":
    st.info("🐦 Post a Tweet using Selenium")
    username = st.text_input("Twitter Username or Email")
    password = st.text_input("Password", type="password")
    tweet = st.text_area("Write your tweet", max_chars=280)

    if st.button("Post Tweet"):
        if not username or not password or not tweet:
            st.error("All fields are required.")
        else:
            speak("Launching browser to post your tweet")
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_argument("--start-maximized")

            driver = webdriver.Chrome(options=chrome_options)

            try:
                driver.get("https://twitter.com/login")
                time.sleep(5)
                driver.find_element(By.NAME, "text").send_keys(username + "\n")
                time.sleep(3)
                driver.find_element(By.NAME, "password").send_keys(password + "\n")
                time.sleep(5)

                tweet_box = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Tweet text']")
                tweet_box.click()
                tweet_box.send_keys(tweet)
                time.sleep(2)

                tweet_btn = driver.find_element(By.XPATH, "//div[@data-testid='tweetButtonInline']")
                tweet_btn.click()

                st.success("✅ Tweet posted successfully!")
                speak("Tweet posted")
            except Exception as e:
                st.error(f"❌ Failed: {e}")
                speak("Tweet posting failed")
            finally:
                time.sleep(5)
                driver.quit()

# ------------------ LINKEDIN POST ------------------
elif choice == "LinkedIn Post":
    st.info("💼 Post on LinkedIn using Selenium")
    email = st.text_input("LinkedIn Email")
    password = st.text_input("LinkedIn Password", type="password")
    post_content = st.text_area("Post Content", height=150)

    if st.button("Post to LinkedIn"):
        if not email or not password or not post_content:
            st.error("Please fill in all fields.")
            speak("Please fill in all fields.")
        else:
            st.info("Launching browser and posting... Please wait.")
            speak("Posting to LinkedIn. Please wait.")

            try:
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                driver = webdriver.Chrome(options=chrome_options)

                driver.get("https://www.linkedin.com/login")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username"))).send_keys(email)
                driver.find_element(By.ID, "password").send_keys(password)
                driver.find_element(By.XPATH, "//button[@type='submit']").click()

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "global-nav-search")))
                driver.get("https://www.linkedin.com/feed/")
                time.sleep(5)

                start_post = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "share-box-feed-entry__trigger"))
                )
                start_post.click()

                post_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ql-editor"))
                )
                post_box.click()
                post_box.send_keys(post_content)
                time.sleep(2)

                post_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Post')]")
                for btn in post_buttons:
                    if btn.is_enabled():
                        btn.click()
                        st.success("✅ LinkedIn post submitted successfully!")
                        speak("LinkedIn post submitted successfully")
                        break
                else:
                    st.error("❌ Couldn't find the Post button.")
                    speak("Post button not found")

                time.sleep(5)
                driver.quit()
            except Exception as e:
                st.error(f"❌ Error occurred: {e}")
                speak("Failed to post on LinkedIn")
                driver.quit()
