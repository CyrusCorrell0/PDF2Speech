import PyPDF2
import requests
import streamlit as st
from openai import OpenAI

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
    st.info("Please add your OpenAI API key to continue.")
else:
    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a PDF!", type=("pdf")
    )

    if uploaded_file:
        # Extract text from PDF
        reader = PyPDF2.PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text.replace('\n', ' ')

        # Split the text into manageable chunks
        charlimit = 4095
        clauses = full_text.split('.')
        chunks = []
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

        # Create an MP3 file
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
                label="Download the generated MP3",
                data=audio_file.read(),
                file_name=mp3_filename,
                mime="audio/mpeg"
            )

        # Add a button to play the MP3
        audio_file_path = mp3_filename
        if st.button("Play PDF"):
            audio_html = f"""<audio controls autoplay>
                            <source src="data:audio/mpeg;base64,{audio_file.read().encode('base64').decode('utf-8')}" type="audio/mpeg">
                            Your browser does not support the audio element.
                          </audio>"""
            st.markdown(audio_html, unsafe_allow_html=True)
