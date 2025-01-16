import PyPDF2
import requests
import streamlit as st
from openai import OpenAI
import unicodedata

# Function to clean extracted text
def clean_text(text):
    return ''.join(c for c in text if unicodedata.category(c)[0] != 'C')
tts_api_url = "https://api.openai.com/v1/audio/speech"

# Show title and description.
st.title("PDF to Speech")
st.write(
    "Tired of silly dyslexia getting in your way? Use PDF to Speech to instantly hear any PDF!"
    "\nTo use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
headers = {
    "Authorization": f"Bearer {openai_api_key}",
    "Content-Type": "application/json"
}

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="\ud83d\udd11")
else:
    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a PDF!", type=("pdf")
    )



    if uploaded_file:
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    cleaned_text = clean_text(text.replace('\n', ' '))
                    full_text += cleaned_text
  
            # Process chunks
            chunks = []
            charlimit = 4095
            clauses = full_text.split('.')
            current_chunk = ""
    
            for clause in clauses:
                clause = clause.strip()
                if clause:
                    potential_chunk = (current_chunk + clause + '.').strip()
                    if len(potential_chunk) <= charlimit:
                        current_chunk = potential_chunk + " "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = clause
    
            if current_chunk:
                chunks.append(current_chunk.strip())
    
            # Generate MP3
            mp3_filename = "output.mp3"
            with open(mp3_filename, "wb") as audio_file:
                for idx, chunk in enumerate(chunks):
                    payload = {
                        "input": chunk,
                        "voice": "onyx",
                        "model": "tts-1"
                    }
                    response = requests.post(tts_api_url, json=payload, headers=headers)
    
                    if response.status_code == 200:
                        audio_file.write(response.content)
                        st.write(f"Processed chunk {idx + 1}/{len(chunks)}")
                    else:
                        st.error(f"Failed to process chunk {idx + 1}. Status: {response.status_code}, Response: {response.text}")
                        break
    
            # Provide a download button
            with open(mp3_filename, "rb") as audio_file:
                st.download_button(
                    label="🎧 Download the generated MP3",
                    data=audio_file.read(),
                    file_name=mp3_filename,
                    mime="audio/mpeg"
                )
  
        except UnicodeEncodeError as e:
          st.error(f"Unicode error: {e}")
