import streamlit as st
from translate import Translator
import google.generativeai as genai
from gtts import gTTS
import base64
import os
import speech_recognition as sr
import requests
from PIL import Image
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use the environment variables
GENAI_API_KEY = "AIzaSyAWICwCFuZoc7tbxOXO_D4qqgjANVfk820"

# Function to query Stable Diffusion API for fashion-related images
def query_stabilitydiff(payload, headers):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

# Configure the Gemini AI with the provided API key
genai.configure(api_key=GENAI_API_KEY)

# Initialize the Gemini AI model
model = genai.GenerativeModel('gemini-1.5-flash')

# Function to translate text
def translate_text(text, dest_language):
    translator = Translator(to_lang=dest_language)
    translation = translator.translate(text)
    return translation

# Function to generate a response using Gemini AI
def generate_gemini_response(prompt):
    response = model.generate_content(prompt)
    return response.text

# Function to convert text to speech and generate a download link
def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts.save("fashion_response.mp3")

    # Read the audio file and encode it to base64
    audio_file = open("fashion_response.mp3", "rb")
    audio_bytes = audio_file.read()
    audio_b64 = base64.b64encode(audio_bytes).decode()
    audio_file.close()
    os.remove("fashion_response.mp3")

    return f'<audio controls autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'

# Function to recognize speech input
def recognize_speech(device_index=None):
    recognizer = sr.Recognizer()
    with sr.Microphone(device_index=device_index) as source:
        st.info("Listening for fashion queries...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.success(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            st.error(f"Sorry, there was an issue with the speech recognition service: {e}")
    return ""

# Map language to ISO 639-1 code
languages_map = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Odia": "or",
    "Urdu": "ur",
    "Chinese": "zh-CN",
    "Korean": "ko",
    "Japanese": "ja",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Italian": "it",
    "Russian": "ru",
    "Arabic": "ar",
    "Dutch": "nl",
    "Portuguese": "pt",
    "Turkish": "tr",
    "Polish": "pl",
    "Swedish": "sv",
    "Vietnamese": "vi",
    "Greek": "el",
    "Thai": "th",
    "Indonesian": "id",
    "Romanian": "ro",
    "Hungarian": "hu",
    "Czech": "cs",
    "Finnish": "fi",
    "Danish": "da",
    "Norwegian": "no",
    "Slovak": "sk",
    "Catalan": "ca",
    "Hebrew": "he",
    "Ukrainian": "uk",
    "Lithuanian": "lt",
    "Slovenian": "sl",
    "Serbian": "sr",
    "Croatian": "hr",
    "Bulgarian": "bg",
    "Farsi": "fa",
    "Estonian": "et",
    "Latvian": "lv",
    "Albanian": "sq",
    "Macedonian": "mk",
    "Afrikaans": "af",
    "Swahili": "sw",
    "Yoruba": "yo",
    "Zulu": "zu",
    "Sesotho": "st",
    "Xhosa": "xh",
    "Somali": "so",
    "Igbo": "ig",
    "Hausa": "ha",
    "Amharic": "am",
    "Corsican": "co",
    "Filipino": "fil",
    "Kurdish": "ku",
    "Luxembourgish": "lb",
    "Malagasy": "mg",
    "Maori": "mi",
    "Nepali": "ne",
    "Pashto": "ps",
    "Samoan": "sm",
    "Scots Gaelic": "gd",
    "Shona": "sn",
    "Sindhi": "sd",
    "Sinhala": "si",
    "Tajik": "tg",
    "Tatar": "tt",
    "Uzbek": "uz",
    "Tongan": "to",
    "Turkmen": "tk",
    "Twi": "tw",
    "Uighur": "ug",
    "Yiddish": "yi",
}

# Sidebar for language selection
selected_language = st.sidebar.selectbox("**Select Your Language**", list(languages_map.keys()))
dest_language = languages_map[selected_language]

# Sidebar details
st.sidebar.markdown(
    """
    <div style="font-size: 20px;">FashionChat💃 Features:</div>
    
        🌐 Multilingual support
        ✏️ Fashion-based text chat
        🔊 Text-to-speech response
    
    
    """, unsafe_allow_html=True)

st.title("FashionChat💃")
st.write("\n")
col1, col2 = st.columns([2, 4])  # Adjust the column widths as needed
with col1:
    st.image("image.png", use_container_width=True)
with col2:
    # Welcome message with fashion-specific features
    st.markdown(f"""
    Welcome to **FashionChat💃**! Here's how you can interact with our fashion expert: \n
    1. **Ask fashion questions✏️**: Type your fashion-related queries and get personalized advice.
    2. **Listen to advice🔊**: After typing your query, click the speaker button to hear expert advice.
    3. **Multilingual support🌐**: Get advice in various languages like English, Hindi, Telugu, and **{len(languages_map)}** more!
               """)

st.write("\n")
if "messages" not in st.session_state:
    st.session_state.messages = []

if "response_text" not in st.session_state:
    st.session_state.response_text = ""
    st.session_state.is_image_response = False

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message:
            st.image(message["image"], caption=message["content"], use_container_width=True)
        else:
            st.markdown(message["content"])

# Handle new user input
prompt = st.chat_input("What's trending in fashion right now?") # Change device_index as needed

if prompt:
    if prompt[0] == '!' or prompt[0:8] == 'generate':
        # Input prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Query Stable Diffusion for fashion images
        headers = {"Authorization": f"Bearer {HUGGING_FACE_TOKEN}"}
        image_bytes = query_stabilitydiff({
            "inputs": prompt,
        }, headers)

        # Return Image
        image = Image.open(io.BytesIO(image_bytes))
        msg = f'Here is a fashion visual related to "{prompt}"'

        # Show Result
        st.session_state.messages.append({"role": "assistant", "content": msg, "image": image})
        st.session_state.is_image_response = True
        st.chat_message("assistant").write(msg)
        st.chat_message("assistant").image(image, caption=prompt, use_container_width=True)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            st.session_state.response_text = generate_gemini_response("Give me the respose straight forward in maximum of two or three lines. make sure to sound like a fashion expert and if the query is nit form fashion related domain, give respose that sound like this is not my domain of expertise in a postive way. If required you are allowed to search the web and respond in more than three but less than 5 lines." + prompt)
            # Translate the response
            if dest_language != 'en':
                translated_response = translate_text(st.session_state.response_text[:400], dest_language)
            else:
                translated_response = st.session_state.response_text
            st.markdown(translated_response)
            st.session_state.messages.append({"role": "assistant", "content": translated_response})
            st.session_state.is_image_response = False

# Add a "Hear response" button to play the response
if st.session_state.response_text and not st.session_state.is_image_response:
    if st.button("Hear response🔊"):
        st.markdown(text_to_speech(translate_text(st.session_state.response_text[:400], dest_language)), unsafe_allow_html=True)
