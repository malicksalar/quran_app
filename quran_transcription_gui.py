import streamlit as st
import speech_recognition as sr
import arabic_reshaper
from bidi.algorithm import get_display
from pydub import AudioSegment
import os

# Function to transcribe audio from a file
def transcribe_audio(file_path):
    try:
        sound = AudioSegment.from_file(file_path)
        wav_file_path = file_path.rsplit('.', 1)[0] + '.wav'
        sound.export(wav_file_path, format='wav')

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_file_path) as source:
            audio_data = recognizer.record(source)
            transcribed_text = recognizer.recognize_google(audio_data, language='ar-SA')
        
        os.remove(wav_file_path)
        return transcribed_text
    except sr.UnknownValueError:
        return "خطأ: لم يتمكن النظام من التعرف على الكلام."
    except sr.RequestError as e:
        return f"خطأ في الاتصال بالخدمة: {e}"
    except Exception as e:
        return f"حدث خطأ: {str(e)}"

# Function to transcribe live audio from the microphone
def transcribe_live_audio():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    
    with mic as source:
        st.write("Start reciting...")
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.listen(source)
        st.write("Transcribing...")
        
        try:
            transcribed_text = recognizer.recognize_google(audio_data, language='ar-SA')
            return transcribed_text
        except sr.UnknownValueError:
            return "خطأ: لم يتمكن النظام من التعرف على الكلام."
        except sr.RequestError as e:
            return f"خطأ في الاتصال بالخدمة: {e}"
        except Exception as e:
            return f"حدث خطأ: {str(e)}"

# Compare transcriptions word by word
def compare_transcriptions(recited_text, correct_text):
    recited_words = recited_text.split()
    correct_words = correct_text.split()
    
    comparison_result = ""
    for recited_word, correct_word in zip(recited_words, correct_words):
        if recited_word == correct_word:
            comparison_result += f"<span style='color:green;'>{recited_word}</span> "
        else:
            comparison_result += f"<span style='color:red;'>{recited_word}</span> "
    
    return comparison_result.strip()

# Main application
def main():
    st.title("Quran Speech to Text")

    # Add custom CSS for Arabic text styling
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Amiri&display=swap');

            .arabic-text {
                font-family: 'Amiri', serif;
                font-size: 28px;
                direction: rtl;
                text-align: right;
                line-height: 1.6;
            }
        </style>
        """, unsafe_allow_html=True)

    # File upload for initial recitation
    uploaded_file = st.file_uploader("Upload your recitation file", type=["mp3", "wav", "flac", "ogg", "aac", "wma"])
    
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp_audio_file", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        if st.button("Transcribe Recitation"):
            # Transcribe the uploaded audio file
            transcribed_text = transcribe_audio("temp_audio_file")

            if transcribed_text.startswith("خطأ"):
                st.markdown(f"<p class='arabic-text' style='color:red;'>{transcribed_text}</p>", unsafe_allow_html=True)
            else:
                reshaped_transcribed_text = arabic_reshaper.reshape(transcribed_text)
                st.markdown(f"<p class='arabic-text' style='color:green;'>{reshaped_transcribed_text}</p>", unsafe_allow_html=True)

                # Option for live recitation
                st.write("Do you want to recite live?")
                recite_option = st.radio("", ("Yes", "No"))

                if recite_option == "Yes":
                    # Record and transcribe live audio
                    st.write("Please recite now...")
                    live_recited_text = transcribe_live_audio()

                    if live_recited_text.startswith("خطأ"):
                        st.markdown(f"<p class='arabic-text' style='color:red;'>{live_recited_text}</p>", unsafe_allow_html=True)
                    else:
                        # Compare live recitation with the transcribed text
                        comparison_result = compare_transcriptions(live_recited_text, transcribed_text)

                        reshaped_comparison_text = arabic_reshaper.reshape(comparison_result)
                        st.markdown(f"<p class='arabic-text'>{reshaped_comparison_text}</p>", unsafe_allow_html=True)
                
                else:  # If the user selects "No"
                    st.write("Thanks for using the Quran Speech to Text Transcriber!")

if __name__ == "__main__":
    main()
