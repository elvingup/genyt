import google.generativeai as genai
import streamlit as st

from env import TOKEN


genai.configure(api_key=TOKEN)

@st.experimental_fragment
@st.cache_resource
def upload_audio_genai(audio_path, TOKEN):
    genai.configure(api_key=TOKEN)
    your_file = genai.upload_file(path=audio_path)
    return your_file

@st.experimental_fragment
def prompt_audio(prompt, audio_file_genai):
    model = genai.GenerativeModel('models/gemini-1.5-pro-latest')
    response = model.generate_content([prompt, audio_file_genai])
    return response

if __name__ == '__main__':
    ...