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
    
    # ✅ Check for Korean curse words first
    flagged_words = [word for word in korean_profanity_list if word in text]

    # ✅ OpenAI Moderation API Check
    response = openai.moderations.create(input=text, model="text-moderation-latest")
    result = response.results[0]
    flagged = result.flagged  # True if inappropriate content is detected
    
    # ✅ Fix: Convert categories to dictionary & handle None values
    categories_dict = result.categories.model_dump()
    flagged_categories = [category for category, score in categories_dict.items() if score is not None and score > 0.5]

    # ✅ If any profanity is found (either from custom list or API), return flagged status
    if flagged_words or flagged:
        return True, flagged_categories, flagged_words  # ✅ Return flagged status, categories, & detected words
    else:
        return False, [], []  # ✅ No flagged words detected


# ✅ Define alternative response suggestion
def suggest_better_response(user_input):
    """Use AI to suggest a better, appropriate response instead of blocking."""
    prompt = f"The user entered inappropriate content: '{user_input}'. Please rephrase it politely and appropriately for the conversation."
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    return response.choices[0].message.content

# ✅ Define chatbot response function
def chatbot_response(conversation_history):
    """Generate chatbot response using OpenAI GPT-4"""
    print("📡 Sending message history to GPT-4:", conversation_history)  # Debugging

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=conversation_history
    )

    chatbot_reply = response.choices[0].message.content
    print("🤖 GPT-4 Response:", chatbot_reply)  # Debugging
    return chatbot_reply

def record_audio(duration=18, samplerate=16000):
    """Records audio from the microphone and saves it as a WAV file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        filename = tmpfile.name
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)  # Mono channel
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(samplerate)

            print("Recording...")
            with sd.InputStream(callback=callback, samplerate=samplerate, channels=1, dtype="int16"):
                for _ in range(int(samplerate / 1024 * duration)):
                    wf.writeframes(q.get())

            print("Recording complete.")
    return filename

def transcribe_audio_whisper_api(audio_path):
    """Send audio file to OpenAI Whisper API and return transcribed text"""
    with open(audio_path, "rb") as audio_file:
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return response.text

def autoplay_audio(audio_path):
    """Plays audio automatically in Streamlit with a 1-second delay before playback."""
    # Read the audio file
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()

    # Encode audio to base64
    encoded_audio = base64.b64encode(audio_bytes).decode()

    # Create HTML for autoplay
    audio_html = f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{encoded_audio}" type="audio/mp3">
    </audio>
    """

    # ⏳ Add a 1-second delay before playing the audio
    time.sleep(1)
    
    # Display autoplay audio in Streamlit using HTML
    st.markdown(audio_html, unsafe_allow_html=True)


def whisper_tts(text):
    """Convert chatbot response to speech using OpenAI's TTS API with a 1-second delay and autoplay."""
    
    # Extract only Korean text using regex
    korean_only_text = re.sub(r"[a-zA-Z0-9\(\)\:\.\,\-]", "", text).strip()
    
    # Ensure non-empty Korean text is passed to TTS
    if korean_only_text:
        response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Choose from: alloy, nova, shimmer, echo
            input=korean_only_text  # Use only Korean text for TTS
        )
        
        # Save the audio response
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        with open(audio_path, "wb") as audio_file:
            audio_file.write(response.content)

        # 🔄 Save the path to session state for persistent display
        st.session_state.audio_files.append(audio_path)

        # ⏳ Keep the 1-second delay before returning the audio path
        time.sleep(1)

        return audio_path
    else:
        print("🚨 No Korean text found for TTS!")
        return None  # Return None if no Korean text is found


# Collect personal information
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "custom_prompts" not in st.session_state:
    st.session_state.custom_prompts = None

# **Step 1: User Info Collection**
if st.session_state.user_info is None:
    st.write("### 📋 Please enter information to customize the Korean conversation.")

    with st.form("user_info_form"):
        name = st.text_input("Name")
        nationality = st.text_input("Nationality")
        native_language = st.text_input("Native Language")
        residence_status = st.radio("Do you live in Korea", ["Yes", "No"])
        # ✅ If "네" is selected, ask about visa details
        if residence_status == "네":
            stay_duration = st.text_input("한국 체류기간 (예: 1년, 6개월)")

        # ✅ Visa Type Dropdown
        visa_options = ["C4", "D2", "D3", "D4", "D10", "E4", "E7", "E8", "E9",
                        "H2", "F1", "F2", "F3", "F4", "F6", "G1", "Others"]

        visa_type = st.selectbox("Visa Type:", visa_options)

        # ✅ If "기타(직접입력)" is selected, allow manual input
        if visa_type == "Others":
            visa_type = st.text_input("Enter Visa Type:")
        else:
            stay_duration = "n/a"
            visa_type = "n/a"
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

# **Step 2: Generate Personalized Prompts**
if st.session_state.user_info and st.session_state.custom_prompts is None:
    st.write("🤖 Building custom conversation topics")

    user_info_text = "\n".join([f"{k}: {v}" for k, v in st.session_state.user_info.items()])
    prompt_text = f"""
    사용자의 개인 정보를 기반으로 한국어와 영어로 대화 주제를 작성해 주세요. 
    예시 : 상사에게 프로젝트 상황 보고하기 / Reporting project status to the boss.
    와 해당 주제에 대한 대화 시작 문장을 작성해 주세요.
    
    첫 번째는 사적인 이야기(취미, 관심사 등), 두번째 대화는 공적인 상황 (직장에서 보고한다던가 등)으로 설정해주세요.
    대화 주제는 한국에서 겪을 가능성이 높은 일상적인 상황이어야 합니다.

    📌 **예시 (출력 형식)**
    - "K드라마 종영 후 의견 나누기:  지난주까지 재밌는 드라마 봤는데, 종영해서 너무 아쉽다."
    - "상사에게 일정이 늦어진다고 말하기 : 팀 프로젝트 일정이 밀려서, 보고 드려야 할 것 같아요."
    - "처음 만난 사람에게 자기소개하기 : 안녕하세요! 저는 [이름]이고, [국적]에서 왔어요."

    **조건:**
    - 대화 주제는 10~15자 내외의 짧은 제목으로 작성해 주세요.
    - 뒤에는 해당 주제에 맞는 자연스러운 첫 번째 문장을 함께 생성하세요.
    - 첫 번째 문장은 대화를 시작하는 자연스러운 한국어 표현이어야 합니다.
    - 너무 형식적인 문어체가 아닌, 실제 대화에서 쓰일 수 있는 구어체로 작성해 주세요.

    사용자가 제공한 정보:
    {user_info_text}

    위 조건을 따라 두 개의 대화 주제 그 대화들을 각각 위한 시작 문장을 생성하세요.
    """

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": prompt_text}]
    )
    custom_prompts = []
    prompt_starters = []

    for line in response.choices[0].message.content.split("\n"):
        if ":" in line and '"' in line:
            topic_part, starter_part = line.split(":", 1)  # Split only at the first colon
            topic = topic_part.replace("-", "").replace('"', '').strip()  # Remove - " and quotes
            starter = starter_part.replace('"', '').strip()  # Remove extra quotes
            
            custom_prompts.append(topic)
            prompt_starters.append(starter)

    st.session_state.custom_prompts = custom_prompts
    st.session_state.prompt_starters = prompt_starters  # Store starting sentences separately

    # ✅ Debugging: Show generated prompts and openings
    print("🛠️ **Debugging Info:**")
    print("📌 AI-Generated Prompts:", st.session_state.custom_prompts)
    print("📢 AI-Generated Opening Sentences:", st.session_state.prompt_starters)
    st.rerun()

    # ✅ Debugging: Show generated prompts and openings

# **Step 3: Select Conversation Topic**
if st.session_state.custom_prompts and st.session_state.prompt_starters:
    st.write("🎯 **대화 주제를 선택하세요**:")

    # ✅ Predefined prompts with corresponding opening sentences
    predefined_prompts = {
        "🛒 옷 고르고 사기 / Buying clothing in a store": "안녕하세요 손님! 무슨 옷을 사고 싶으신가요? Hello! What clothes are you looking for? (Annyeonghaseyo sonnim! Musun otsul sago shipshingayo?)",
        "🗺️ 방향 묻기 / Asking for directions ": "안녕하세요. 어디 가고 싶으신 곳 있나요? Hello. Are you looking for directions (Annyeonghaseyo. Eodi gago sipshin got itnayo?)",
        "🎉 재미있는 이벤트에 대해서 말해보기 / Talk about a fun event": "어제 무슨 재미있는 일이 있었나요? What fun event did you have yesterday (Eojae Museun Jaemiissneun Iri Isseotnayo?)",
    }

    # ✅ AI-generated prompts (ensures correct mapping)
    ai_prompts = {
        "🆕 " + st.session_state.custom_prompts[0]: st.session_state.prompt_starters[0],
        "🆕 " + st.session_state.custom_prompts[1]: st.session_state.prompt_starters[1]
    }

    # ✅ Merge predefined & AI-generated prompts
    prompts = {**predefined_prompts, **ai_prompts}

    # ✅ User selects a topic
    selected_prompt = st.selectbox("대화를 시작할 주제를 선택하세요:", list(prompts.keys()))

    if st.button("🔄 대화 시작하기"):
        #st.write(f"🎯 **Selected Prompt:** {selected_prompt}")

        # ✅ Get chatbot's first response (opening sentence)
        chatbot_opening = prompts[selected_prompt] if selected_prompt in prompts else "이 주제에 대해 이야기해볼까요?"

        #st.write(f"📢 **Chatbot Opening:** {chatbot_opening}")

        # ✅ Store conversation history
        st.session_state.conversation_history = [
            {"role": "system", "content": "당신은 친절한 한국어 대화 파트너입니다. "
                                          "실제 생활에서 자연스럽게 대화를 나누듯이 응답하세요. "
                                          "너무 형식적인 문어체가 아닌 구어체로 대답하세요. "
                                          "사용자가 대화에 참여하도록 격려하세요. "
                                          "답변은 2~3문장으로 짧고 명확하게 하세요."\
                                          "항상 존중하듯이 존댓말로 하세요."
                                          "답변을 해 주신 뒤에는 영어로 한국어 phonetic과 뜻을 적어 주세요."},
            {"role": "assistant", "content": chatbot_opening}
        ]


        # ✅ Ensure GPT response is fully received before TTS
        if chatbot_opening:
            # ⏳ Add a delay to ensure GPT's response is fully processed
            time.sleep(1)  # Delay to make sure GPT response is fully received

            # ✅ Generate TTS audio after delay
            tts_audio = whisper_tts(chatbot_opening)

            # ✅ Play TTS audio with an additional delay for smooth timing
            if tts_audio:
                time.sleep(1)  # ⏳ Extra delay before playback to enhance timing
                st.audio(tts_audio, format="audio/mp3", autoplay=True)

        else:
            st.write("🚨 **TTS Failed to Generate Audio!**")

        # ✅ Store message history
        st.session_state.last_played_message = chatbot_opening
        st.session_state.chat_active = True
        st.rerun()

# **Step 4: Conversation Mode **
if st.session_state.chat_active:
    st.write("💬 **대화 기록**:")

    # ✅ Print all session state for debugging
    print("🛠️ Current session_state:", dict(st.session_state))

    # ✅ Initialize TTS playback control in session state
    if "tts_playback" not in st.session_state:
        st.session_state.tts_playback = False  # Default: No playback until chatbot speaks

    if "last_played_message" not in st.session_state:
        st.session_state.last_played_message = ""  # Stores the last chatbot message played in TTS

    # ✅ Only play TTS for the latest chatbot message to prevent replays
    for i, msg in enumerate(st.session_state.conversation_history):
        if msg["role"] == "user":
            st.markdown(f"👤 **You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"🤖 **Chatbot:** {msg['content']}")

            # ✅ Only play TTS for the latest assistant message & prevent replay during recording
            if i == len(st.session_state.conversation_history) - 1 and st.session_state.tts_playback:
                if msg["content"] != st.session_state.last_played_message:
                    tts_audio = whisper_tts(msg["content"])
                    autoplay_audio(tts_audio)

                    # ✅ Store the last played message to prevent replaying
                    st.session_state.last_played_message = msg["content"]

    st.write(f"⏳ **진행 상황:** {st.session_state.get('response_count', 0) + 1} / 5 회")

    if st.session_state.response_count < 5:
        if st.button("🎙️ 음성 녹음 시작 (15초)"):
            st.session_state.tts_playback = False  # Disable TTS while recording
            st.session_state.last_played_message = ""  # Reset last played message to avoid replays
            with st.spinner("🎤 녹음 중... 15초 동안 말해주세요."):
                recorded_audio_path = record_audio()  # Replace with actual recording function

            st.write("📡 텍스트로 변환 중...")
            korean_text = transcribe_audio_whisper_api(recorded_audio_path)

            # 🚨 Check for profanity & get flagged categories and words
            flagged, flagged_categories, flagged_words = check_profanity(korean_text)

            if flagged:
                st.session_state.strike_count += 1
                # 🚨 Show warning with flagged words & categories
                warning_message = f"⚠️ **경고!** 부적절한 표현이 감지되었습니다.\n"
                if flagged_words:
                    warning_message += f"🚨 감지된 단어: {', '.join(flagged_words)}\n"
                if flagged_categories:
                    warning_message += f"📌 감지된 유형: {', '.join(flagged_categories)}\n"

                warning_message += f"⚠️ 앞으로 {3 - st.session_state.strike_count}번 더 경고를 받으면 대화가 종료됩니다."
                st.warning(warning_message)

                if st.session_state.strike_count >= 3:
                    st.write("🚨 **부적절한 표현이 여러 번 감지되었습니다.**")
                    if st.button("🔄 새로운 대화 시작하기"):
                        st.session_state.chat_active = False
                        st.session_state.response_count = 0
                        st.session_state.conversation_history = []
                        st.session_state.custom_prompts = None
                        st.session_state.user_info = None
                        st.session_state.strike_count = 0  # Reset warnings
                        st.rerun()
                    st.stop()
            else:
                # ✅ If no profanity, proceed normally
                st.write(f"👤 **You:** {korean_text}")
                st.session_state.conversation_history.append({"role": "user", "content": korean_text})

                chatbot_reply = chatbot_response(st.session_state.conversation_history)
                st.session_state.conversation_history.append({"role": "assistant", "content": chatbot_reply})

                # 🔄 Debugging print to ensure response count updates
                print("🛠️ Before Increment: response_count =", st.session_state.response_count)
                st.session_state.response_count += 1  # ✅ Increment response count here
                print("🛠️ After Increment: response_count =", st.session_state.response_count)

                st.session_state.tts_playback = True  # ✅ Enable TTS playback for chatbot response
                st.session_state.last_played_message = ""  # ✅ Reset last played message to ensure it plays once

                # ✅ Only rerun when necessary
                if st.session_state.response_count < 5:
                    st.rerun()

            # ✅ Debugging: Ensure count updates correctly
            st.write(f"🧮 **현재 대화 횟수:** {st.session_state.response_count} / 5")
        else:
            print("🛠️ '음성 녹음 시작' 버튼이 클릭되지 않음.")  # Debug print for button click check
    else:
        st.write("🎉 **대화가 끝났어요! 5번의 대화를 완료했습니다.**")
        st.write("🎧 **저장된 음성 파일들:**")
        print("🛠️ End of Conversation Block Reached - Displaying New Conversation Button")

    for i, audio_path in enumerate(st.session_state.audio_files, start=1):
        st.audio(audio_path, format="audio/mp3", start_time=0)
        st.write(f"🔊 **응답 {i}의 음성 파일:**")

    # ✅ Ensure the button appears here
    if st.button("🔄 새로운 대화 시작하기"):
        print("🛠️ '새로운 대화 시작하기' 버튼 클릭됨!")  # Debug print for button click
        st.session_state.chat_active = False
        st.session_state.response_count = 0
        st.session_state.conversation_history = []
        st.session_state.custom_prompts = None
        st.session_state.user_info = None
        st.session_state.strike_count = 0  # Reset warnings
        print("🛠️ Reset all session state variables for new conversation.")  # Debug print
        st.rerun()