import re
import subprocess
import os
import json

from pytube import YouTube
import streamlit as st
import whisper
import semchunk
import tiktoken
import textwrap
from IPython.display import Markdown


@st.experimental_fragment
def download_audio(link, output_path, filename):
    youtubeObject = YouTube(link)
    # youtubeObject = youtubeObject.streams.get_highest_resolution()
    youtubeObject = youtubeObject.streams.get_audio_only()
    try:
        youtubeObject.download(
            output_path=output_path,
            filename=filename,
            skip_existing=True
        )
    except:
        print("An error has occurred")
    print("Download is completed successfully")

@st.experimental_fragment
def download_video_hd(link):
    youtubeObject = YouTube(link)
    youtubeObject = youtubeObject.streams.get_highest_resolution()
    try:
        youtubeObject.download()
    except:
        print("An error has occurred")
    print("Download is completed successfully")

@st.cache_data
def get_video_len(url):
    yt = YouTube(url)
    stream = yt.streams.first()
    return {
        'title': yt.title,
        'author': yt.author,
        'keywords': yt.keywords,
        'captions': yt.captions,
        'channel_url': yt.channel_url,
        'publish_date': yt.publish_date,
        'video_id': yt.video_id,
        'metadata': yt.metadata.raw_metadata,
        'video description: ': yt.description,
        'rating': yt.rating,
        'length': yt.length,
        'views': yt.views,
    }

@st.cache_data
def extrair_metadados_youtube(url):
    """
    Extrai o nome e a duração em minutos de um vídeo do YouTube a partir da URL.

    Args:
        url: A URL do vídeo do YouTube.

    Returns:
        Uma tupla contendo o nome e a duração em minutos, ou None se a URL for inválida.
    """

    # Verifica se a URL é válida
    if not re.match(r"https?://(www\.)?youtube\.com/watch\?v=.*", url):
        return None

    # Constrói a URL da API do YouTube
    api_url = f"https://www.youtube.com/oembed?url={url}&format=json"

    # Faz a requisição à API
    try:
        import requests
        response = requests.get(api_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a API do YouTube: {e}")
        return None

    # Analisa a resposta JSON
    try:
        metadados = response.json()
        # nome = metadados['title']
        # duracao_segundos = metadados['duration']
        # duracao_minutos = round(duracao_segundos / 60, 2)  # Calcula a duração em minutos com 2 casas decimais
        return metadados
    except (ValueError, KeyError) as e:
        print(f"Erro ao analisar a resposta da API: {e}")
        return None

@st.cache_data
def get_video_description(url):
    youtube = YouTube(url)
    stream = youtube.streams.first()
    desc = youtube.description
    return desc

@st.experimental_fragment
def convert_mp4_to_mp3(input_file, output_file):
  """
  Converts an MP4 video file to an MP3 audio file using ffmpeg.

  Args:
      input_file (str): Path to the input MP4 video file.
      output_file (str): Path to the output MP3 audio file.
  """
  command = ["ffmpeg", "-i", input_file, "-vn", "-acodec", "libmp3lame", output_file]
  subprocess.run(command, check=True)

@st.experimental_fragment
@st.cache_data
def get_transcription(audio_path):
    #Check cache
    id = audio_path.split('_')[-1].split('.')[0]
    transcription_path = f'data/transcript_{id}.json'
    if not os.path.exists(transcription_path):
        modelo_audio_text = whisper.load_model('base')
        resposta = modelo_audio_text.transcribe(audio_path)
        with open(transcription_path, mode='w', encoding='utf8') as f:
            f.write(json.dumps(resposta, indent=4))
        return resposta['text']
    else:
        with open(transcription_path, mode='r', encoding='utf8') as f:
            response = json.loads(f.read())['text']
        return response

@st.cache_data
@st.experimental_fragment
def split_text(text) -> list:
    chunk_size = 1000 # A low chunk size is used here for demo purposes.
    encoder = tiktoken.encoding_for_model('gpt-4')
    token_counter = lambda text: len(encoder.encode(text)) # `token_counter` may be swapped out for any function capable of counting tokens.
    text_splitted = semchunk.chunk(text, chunk_size=chunk_size, token_counter=token_counter)
    print(len(text_splitted))
    return text_splitted

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

if __name__ == '__main__':
    ...