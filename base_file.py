import os
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

# Set the path to the service account key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'quran-recitation-ai-a16ce3a5144a.json'



# TODO(developer): Update and un-comment below line
PROJECT_ID = "quran-recitation-ai"

# Instantiates a client
client = SpeechClient()

# Reads a file as bytes
with open("Surah Ikhlas.mp3", "rb") as f:
    audio_content = f.read()

config = cloud_speech.RecognitionConfig(
    auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
    language_codes=["ar-SA"],
    model="long",
)

request = cloud_speech.RecognizeRequest(
    recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
    config=config,
    content=audio_content,
)

# Transcribes the audio into text
response = client.recognize(request=request)

with open("output.txt", "w", encoding="utf-8") as f:
        # Write each transcription result to the file
        for result in response.results:
            transcript = result.alternatives[0].transcript
            confidence = result.alternatives[0].confidence
            f.write(f"Transcript: {transcript}\n")
            f.write(f"Transcript: {confidence}\n")
            # print(f"Transcript: {transcript}")