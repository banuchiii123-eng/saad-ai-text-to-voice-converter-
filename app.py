
import streamlit as st
import os
import tempfile
from groq import Groq
from gtts import gTTS
from io import BytesIO

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Saad/AI Text to Voice",
    page_icon="🎙️",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
.title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #00D4AA;
}
.subtitle {
    text-align: center;
    color: #AAAAAA;
    font-size: 16px;
}
.stButton>button {
    background-color: #00D4AA;
    color: black;
    border-radius: 10px;
    font-weight: bold;
    width: 100%;
    border: none;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown(
    '<div class="title">🎙️ Saad/AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI Powered Text to Voice Converter</div>',
    unsafe_allow_html=True
)

st.write("")
st.divider()

st.markdown("### 📝 Enter Your Text")

# ---------------- API KEY ----------------

api_key = st.secrets.get(
    "GROQ_API_KEY",
    os.getenv("GROQ_API_KEY", "")
)

# ---------------- LANGUAGE OPTIONS ----------------

languages = {
    "English": "en",
    "Urdu": "ur",
    "Arabic": "ar",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Chinese": "zh-cn",
    "Japanese": "ja",
    "Korean": "ko",
    "Turkish": "tr",
    "Russian": "ru",
    "Bengali": "bn",
    "Punjabi": "pa",
    "Persian": "fa",
    "Indonesian": "id"
}

# ---------------- INPUT ----------------

text_input = st.text_area(
    "Write or paste your text here:",
    height=200,
    placeholder="Enter your text here..."
)

col1, col2 = st.columns(2)

with col1:
    language = st.selectbox(
        "🌍 Select Language",
        list(languages.keys())
    )

with col2:
    speed = st.select_slider(
        "⚡ Speech Speed",
        options=["Slow", "Normal", "Fast"],
        value="Normal"
    )

# ---------------- VOICE OPTIONS ----------------

voice_options = {
    "Female": "hannah",
    "Male": "troy"
}

voice = st.selectbox(
    "🎤 Select Voice",
    list(voice_options.keys())
)

# ---------------- AI TEXT IMPROVEMENT ----------------

improve_text = st.checkbox(
    "✨ Improve text using Groq AI",
    value=False
)

# ---------------- GENERATE BUTTON ----------------

if st.button("🚀 Generate Voice"):

    if not text_input.strip():
        st.warning("Please enter some text first.")

    else:

        final_text = text_input.strip()

        try:

            # AI TEXT IMPROVEMENT
            if improve_text:

                if not api_key:
                    st.error("Please configure your Groq API key.")
                    st.stop()

                client = Groq(api_key=api_key)

                with st.spinner("AI is improving your text..."):

                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "Improve the given text for natural "
                                    "speech. Keep its original language "
                                    "and meaning. Return only the "
                                    "improved text."
                                )
                            },
                            {
                                "role": "user",
                                "content": final_text
                            }
                        ],
                        temperature=0.5
                    )

                    final_text = (
                        response.choices[0].message.content.strip()
                    )

                st.success("Text improved successfully!")

                st.markdown("### ✨ Improved Text")
                st.write(final_text)

            # SPEED SETTINGS
            speed_values = {
                "Slow": 0.8,
                "Normal": 1.0,
                "Fast": 1.2
            }

            speech_speed = speed_values[speed]

            # AUDIO GENERATION
            with st.spinner("Generating your voice..."):

                audio_bytes = None
                audio_type = "audio/mpeg"

                # GROQ TTS: ENGLISH AND ARABIC
                if language in ["English", "Arabic"]:

                    if not api_key:
                        st.error("Please add your Groq API key.")
                        st.stop()

                    # Groq Orpheus currently supports short
                    # input segments (up to 200 characters).
                    if len(final_text) <= 200:

                        client = Groq(api_key=api_key)

                        tts_model = (
                            "canopylabs/orpheus-v1-english"
                            if language == "English"
                            else "canopylabs/orpheus-arabic-saudi"
                        )

                        selected_voice = (
                            voice_options[voice]
                            if language == "English"
                            else ("noura" if voice == "Female" else "fahad")
                        )

                        speech_response = client.audio.speech.create(
                            model=tts_model,
                            voice=selected_voice,
                            input=final_text,
                            response_format="wav",
                            speed=speech_speed
                        )

                        with tempfile.NamedTemporaryFile(
                            suffix=".wav",
                            delete=False
                        ) as temp_file:

                            temp_path = temp_file.name

                        try:
                            speech_response.write_to_file(temp_path)

                            with open(temp_path, "rb") as file:
                                audio_bytes = file.read()

                            audio_type = "audio/wav"

                        finally:
                            if os.path.exists(temp_path):
                                os.remove(temp_path)

                    else:
                        st.info(
                            "Long text detected. Using multilingual "
                            "speech generation."
                        )

                # MULTILINGUAL FALLBACK
                if audio_bytes is None:

                    tts = gTTS(
                        text=final_text,
                        lang=languages[language],
                        slow=(speed == "Slow")
                    )

                    audio_buffer = BytesIO()

                    tts.write_to_fp(audio_buffer)

                    audio_bytes = audio_buffer.getvalue()

                    audio_type = "audio/mpeg"

            # ---------------- OUTPUT ----------------

            st.success("🎉 Voice generated successfully!")

            st.markdown("### 🔊 Your Generated Voice")

            st.audio(
                audio_bytes,
                format=audio_type
            )

            file_extension = (
                "wav" if audio_type == "audio/wav" else "mp3"
            )

            st.download_button(
                label="⬇️ Download Audio",
                data=audio_bytes,
                file_name=f"saad_ai_voice.{file_extension}",
                mime=audio_type
            )

        except Exception as e:

            st.error(
                f"Something went wrong: {str(e)}"
            )

# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    "<center>Made with ❤️ by Saad/AI</center>",
    unsafe_allow_html=True
)
