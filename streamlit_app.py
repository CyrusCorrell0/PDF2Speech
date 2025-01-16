import PyPDF2
import requests
import streamlit as st
from openai import OpenAI
tts_api_url = "https://api.openai.com/v1/audio/speech"

# Show title and description.
st.title("📄 PDF to Speech")
st.write(
    "Tired of silly dyslexia getting in your way? Use PDF to Speech to instantly hear any PDF!"
    "\nTo use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
headers = {
    "Authorization": f"Bearer {openai_api_key}",
    "Content-Type": "application/json"
}
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a PDF!", type=("pdf")
    )

'''    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )
'''
    charlimit = 4095
    ############################################
    # Extract text from PDF
    
    if not off: 
        with open(uploaded_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text.replace('\n', ' ')

        # Split the text into sentences. 
        # Here, we assume sentences end with '.' but you may add more delimiters if needed.
        clauses = full_text.split('.')
    
        for i,clause in enumerate(clauses):
            if len(clause) > charlimit:
                clauses[i] = clause[:charlimit]
                clauses.insert(i+1, clause[charlimit:])
    
    
        chunks = []
        current_chunk = ""
    
        for i, clause in enumerate(clauses):
            # Add the sentence and a period back (except for possibly the last if empty)
            clause = clause.strip()
            if clause:
                potential_chunk = (current_chunk + clause + '.').strip()
                
                if len(potential_chunk) <= charlimit:
                    current_chunk = potential_chunk + " "
                else:
                    # Current sentence would exceed limit, store the current_chunk and start a new one
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = clause
                
        # Append any remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
    
        # 'chunks' now contains your text divided into segments of ≤4095 characters, each ending at a sentence boundary.
        for idx, ch in enumerate(chunks):
            print(f"Chunk {idx+1} ({len(ch)} chars):\n{ch}\n")
    
        # Assuming you've already extracted your chunks from the previous code snippet
        # and that 'chunks' is a list of text chunks.
    
    else:
        chunks = []
        length = len(content)//charlimit #find chunks
        j = 0
        for i in range(length): #for each chunk
            current_chunk = content[j:j+charlimit]
            j += charlimit
            chunks.append(current_chunk)
    
    if uploaded_file:
        #MAKE STREAM
        # Process the uploaded file and question.
        with open(stream, "wb") as f:
        for chunk in chunks:  
            payload = {
                "input": chunk,        # use "input" instead of "text"
                "voice": "onyx",             # make sure voice is all lowercase and valid
                "model": "tts-1"
            }
            response = requests.post(tts_api_url, json=payload, headers=headers) # make api call

        if response.status_code == 200:
            # Assuming the API returns binary audio data directly
            f.write(response.content)
            print("Done")
        else:
            print(f"Failed to retrieve TTS audio. Status code: {response.status_code}, Response: {response.text}")
            break

     '''   # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )
'''
        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)
