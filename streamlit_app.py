import streamlit as st
import soundfile as sf
import numpy as np
from io import BytesIO
from pydub import AudioSegment
from st_audiorec import st_audiorec  # Import the audio recording component
import os
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'quran-recitation-ai-a16ce3a5144a.json'
PROJECT_ID = "quran-recitation-ai"
client = SpeechClient()

def transcribe_audio(file_path):
   config = cloud_speech.RecognitionConfig(
      auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
      language_codes=["ar-SA"],
      model="long",
   ) 

   request = cloud_speech.RecognizeRequest(
      recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
      config=config,
      content=file_path,
   )

# Transcribes the audio into text
   response = client.recognize(request=request)
   return response

def convert_to_mp3(audio_bytes, format):
   audio_segment = AudioSegment.from_file(BytesIO(audio_bytes), format=format)
   wav_io = BytesIO()
   audio_segment.export(wav_io, format="wav", codec="pcm_s16le")  # Convert to LINEAR16
   wav_io.seek(0)  # Reset buffer position to the start
   return wav_io


# Title of the app
st.title("Audio Recorder and Uploader")

# Sidebar
st.sidebar.title("Options")

# Use session_state to preserve file upload and recording between interactions
if "uploaded_audio" not in st.session_state:
   st.session_state.uploaded_audio = None
if "recorded_audio" not in st.session_state:
   st.session_state.recorded_audio = None

# Button to record audio using st_audiorec
st.sidebar.write("Record Audio:")
record_audio = st_audiorec()

# If audio is recorded, save it to session_state and reset the uploaded file
if record_audio is not None:
   st.session_state.recorded_audio = record_audio
   st.session_state.uploaded_audio = None  # Reset uploaded audio if a recording is made

# Logic for uploading audio
uploaded_file = st.sidebar.file_uploader("Upload an audio file", type=["wav", "mp3"])
resetter = st.sidebar.button("Reset")
if resetter:
   st.rerun(scope="app")

# If a file is uploaded, store it in session_state and reset the recorded audio
if uploaded_file is not None:
   st.session_state.uploaded_audio = uploaded_file
   st.session_state.recorded_audio = None  # Reset recorded audio if a file is uploaded

# Display the recorded audio if available and only if no file was uploaded
if st.session_state.recorded_audio is not None:
   st.write("Audio for Transcription (Recorded):")
   st.audio(st.session_state.recorded_audio, format="audio/wav")
   mp3_audio = convert_to_mp3(st.session_state.recorded_audio, format="wav")
   mp3_audio = mp3_audio.read()
   with st.spinner("Transcribing Using Google Speech-to-Text..."):
      transcribed_text = transcribe_audio(mp3_audio)
      for i in transcribed_text.results:
         st.write(i.alternatives[0].transcript)
    

# Display the uploaded audio if available and only if no recording was made
elif st.session_state.uploaded_audio is not None:
   st.write("Audio for Transcription (Uploaded):")
   audio_bytes = st.session_state.uploaded_audio.read()
   audio_data = BytesIO(audio_bytes)
   file_format = st.session_state.uploaded_audio.name.split(".")[-1]

   # Load audio using pydub for format compatibility
   audio_segment = AudioSegment.from_file(audio_data, format=st.session_state.uploaded_audio.name.split(".")[-1])
   mp3_audio = convert_to_mp3(audio_bytes, format=file_format)
   mp3_audio = mp3_audio.read()

   # Display information about the file
   st.audio(audio_bytes, format=f"audio/{st.session_state.uploaded_audio.name.split('.')[-1]}")

   # Transcribe the audio
   with st.spinner("Transcribing Using Google Speech-to-Text..."):
      transcribed_text = transcribe_audio(mp3_audio)
      for i in transcribed_text.results:
         st.write(i.alternatives[0].transcript)
    

# If no action, display default message
if st.session_state.uploaded_audio is None and st.session_state.recorded_audio is None:
   st.write("Click on one of the buttons to record or upload audio.")
