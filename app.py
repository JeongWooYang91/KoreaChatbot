import openai
import base64  
import streamlit as st
import numpy as np
import queue
import tempfile
import wave
import time
import re
import os
from dotenv import load_dotenv  # ✅ Import dotenv
from pydub import AudioSegment
import sounddevice as sd
from audiorecorder import audiorecorder

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Get API keys and secrets
openai.api_key = os.getenv("OPENAI_API_KEY")
prompt_text = os.getenv("AI_PROMPT_TEXT")
korean_profanity_list = os.getenv("KOREAN_PROFANITY", "").split(",")

if "audio_files" not in st.session_state:
    st.session_state.audio_files = []  # To keep track of all audio files

# ✅ Debugging: Check if secrets are loaded
if openai.api_key:
    print("✅ API Key loaded successfully.")
else:
    print("❌ Failed to load API Key!")

if prompt_text:
    print("✅ Prompt text loaded successfully.")
else:
    print("❌ Failed to load prompt text!")

if korean_profanity_list:
    print("✅ Profanity list loaded successfully.")
else:
    print("❌ Failed to load profanity list!")

# Audio queue for real-time recording
q = queue.Queue()

# 🔹 Initialize session state variables **at the start**
if "chat_active" not in st.session_state:
    st.session_state.chat_active = False
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "response_count" not in st.session_state:
    st.session_state.response_count = 0
if "strike_count" not in st.session_state:
    st.session_state.strike_count = 0  # Track user warnings
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "custom_prompts" not in st.session_state:
    st.session_state.custom_prompts = None

# Profanity warning system (3 strikes)
if "strike_count" not in st.session_state:
    st.session_state.strike_count = 0  # Track user warnings

def callback(indata, frames, time, status):
    """Callback function to store audio data"""
    if status:
        print(status)
    q.put(indata.copy())

# ✅ Define OpenAI Moderation API function
def check_profanity(text):
    """Check for inappropriate content using a custom Korean profanity list & OpenAI Moderation API."""
    
    korean_profanity_list = [
        "fuck", "retard", "son of a bitch", "fck", "retard", "dick", "get lost", "damn", "crazy", "stupid",
        "idiot", "mom", "dad", "your mom", "shut up", "fuck you", "die", "get lost", "crazy bastard", "crazy bitch",
        "bitch", "bastard", "fuck", "asshole", "slut", "kill", "beat up", "eat shit", "blockhead", "whore",
        "bastard", "freak", "moron", "stupid", "mouth", "damn", "bastard", "troublemaker",
        "fucking bastard", "coward", "chicken", "coward", "idiot", "retard", "fck",
        "loser", "kimchi girl", "korean man", "korean woman", "old geezer", "moon disaster", "sex", "yoon bitch", "yoon disaster",
        "porn", "masturbate", "jerk off", "pussy", "dickhead", "fucking", "jap", "nigger", "muslim bitch", "fucking gay"
    ]
    
    # ✅ Check for Korean curse words first
    flagged_words = [word for word in korean_profanity_list if word in text]

    # ✅ OpenAI Moderation API Check
    response = openai.moderations.create(input=text, model="text-moderation-latest")
    result = response.results[0]
    flagged = result.flagged  # True if inappropriate content is detected
    
    categories_dict = result.categories.model_dump()
    flagged_categories = [category for category, score in categories_dict.items() if score is not None and score > 0.5]

    if flagged_words or flagged:
        return True, flagged_categories, flagged_words
    else:
        return False, [], []

# ✅ Define alternative response suggestion
def suggest_better_response(user_input):
    """Use AI to suggest a better, appropriate response instead of blocking."""
    prompt = f"The user entered inappropriate content: '{user_input}'. Please rephrase it politely and appropriately for the conversation."
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content

st.title("🗣️ Personalized Korean Conversation Tutor")

# **Step 1: User Info Collection**
if st.session_state.user_info is None:
    st.write("### 📋 Please enter information to customize the Korean conversation.")

    with st.form("user_info_form"):
        name = st.text_input("Name")
        nationality = st.text_input("Nationality")
        native_language = st.text_input("Native Language")
        residence_status = st.radio("Living in Korea", ["Yes", "No"])
        stay_duration = st.text_input("Duration of Stay in Korea (e.g., 1 year, 6 months)")
        visa_type = st.text_input("Visa Type (e.g., Tourist Visa, Work Visa, Student Visa)")
        industry = st.text_input("Industry (e.g., IT, Education, Healthcare)")
        work_experience = st.text_input("Work Experience in the Industry")
        korean_test_score = st.text_input("Korean Test Score (leave blank if none)")
        korean_study_duration = st.text_input("Duration of Korean Study (e.g., 2 years)")
        interests = st.text_input("Interests (e.g., Travel, History, Food)")
        hobbies = st.text_input("Hobbies (e.g., Soccer, Reading, Gaming)")
        
        agree = st.checkbox("📜 Consent for Data Collection: This information will only be used to generate personalized conversation topics.", value=True)
        
        submitted = st.form_submit_button("Submit")

    if submitted and agree:
        st.session_state.user_info = {
            "Name": name,
            "Nationality": nationality,
            "Native Language": native_language,
            "Living in Korea": residence_status,
            "Duration of Stay": stay_duration,
            "Visa Type": visa_type,
            "Industry": industry,
            "Work Experience": work_experience,
            "Korean Test Score": korean_test_score,
            "Duration of Korean Study": korean_study_duration,
            "Interests": interests,
            "Hobbies": hobbies,
        }
        st.rerun()
