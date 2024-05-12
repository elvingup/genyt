import os
import streamlit as st

# from embedder import *
from generator import *
from utils import *

from env import TOKEN


# -----------------------------------------------------------------------------------------------

st.set_page_config(page_title='Genyt Explorer', page_icon=None, 
    layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* top ribbon */
    .css-1dp5vir {
        /*background-image: linear-gradient(90deg, rgb(0, 30, 98), rgb(255, 253, 128));*/
        background-image: linear-gradient(90deg, rgb(0, 30, 98), rgb(228, 124, 119));
        height:0.8rem
    }

    /* alinhar sidebar ao height do ribbon */
    div[data-testid*="stSidebarUserContent"] {
        padding-top:0.8rem
    }


    /* Reduzir o espaçamento superior do conteúdo */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0.8rem
    }
    </style>    
    """,unsafe_allow_html=True)

# -----------------------------------------------------------------------------------------------

if not os.path.exists("data"):
    os.makedirs('data', exist_ok=True)

with st.sidebar:
    st.markdown('# GenYT')

    # st.image('.streamlit/logo.jpeg', width=200)
    with st.container(border=True):
        if st.radio('**1)** Modo de seleção', ['Quero inserir um link','Selecionar um exemplo']) == 'Quero inserir um link':
            url = st.text_input('**2)** Insira o URL do video do Youtube', value='https://www.youtube.com/watch?v=sal78ACtGTc')
        else:
            opts = ['https://www.youtube.com/watch?v=94yuIVdoevc', 'https://www.youtube.com/watch?v=sal78ACtGTc']
            url = st.selectbox('**2)** Insira o URL do video do Youtube', opts, index=None, placeholder="Selecion um link")
    
    if url:
        with st.expander('**3)** Dados do vídeo selecionado', expanded=True):
            div_video = st.container()
            div_metadata = st.container()
            mostrar_mais = st.toggle('Mostrar mais', value=False)
        
        if mostrar_mais:
            with st.expander('Metadados', expanded=False):
                div_mostrarmais = st.container()

    div_info = st.container()

 # --------------------------------------------------------------------------
st.markdown('ㅤ')
# st.markdown('#### O que é GenYT ?')
with st.expander('#### O que é Genyt ?', expanded=True):
    st.markdown('GenYT é uma assistente inteligente com o poder de combinar o LLM generativo do Google GeminiAI com videos do YouTube \
            para oferecer uma experiência de aprendizado imersiva e interativa. \n \
            \n Ela permite assistir, apenas ouvir ou ler qualquer vídeo, e \
            o mais importante, interagir com o Gemini para fazer perguntas sobre o conteúdo. \n\
            \n Siga o passo a passo no painel à esquerda para começar.')


if url:
    video_metadata = get_video_len(url)
    video_len = video_metadata['length']/60
    video_description = video_metadata['video description: ']
    desc = get_video_description(url)
    audio_filename=f'audio_{video_metadata['video_id']}.mp3'
    transcription_filename=f'data/transcript_{video_metadata['video_id']}.json'
    audio_path=f'data/{audio_filename}'

    video_metadata_yt = extrair_metadados_youtube(url)
    thumbnail_url = video_metadata_yt['thumbnail_url']
    video_title = video_metadata_yt['title']
    video_author = video_metadata_yt['author_name']
    video_channel = video_metadata_yt['author_url']
    
    div_metadata.markdown(f"""
        # {video_title}
        **Autor**: `{video_author}` \n
        **Canal**: {video_channel} \n
        **Descrição**:
        """)
    div_metadata.markdown(video_description)
        
    if div_video.toggle('Preview video', value=False): div_video.video(url)
    else: div_video.image(thumbnail_url, use_column_width=True)
    
    if mostrar_mais:
        if video_metadata: div_mostrarmais.json(video_metadata)
        if video_metadata_yt: div_mostrarmais.json(video_metadata_yt)

   

    # --------------------------------------------------------------------------
    # st.markdown('---')
    # st.markdown('#### 4) Analisar o conteúdo do vídeo')
    with st.expander('#### 4) Analisar o conteúdo do vídeo', expanded=True):
        if os.path.exists(audio_path):
            st.markdown('##### Ouvir')
            st.audio(audio_path)
        else:
            st.info('É a primeira vez que você selecionou esse vídeo, clique no botão abaixo para analisar o conteúdo.')
            if st.button('Analisar!'):
                with st.info('Baixando o audio do video'):
                    download_audio(url, 'data', audio_filename)
                st.audio(audio_path)
    
        if os.path.exists(audio_path):
                
            if os.path.exists(transcription_filename):
                text_transcription=get_transcription(audio_path)
                st.markdown('##### Ler')
                st.text_area(label='Transcrição',value=text_transcription)
            else:
                if st.button('Se preferir ler, clique aqui para transcrever (a primeira vez pode lever um tempinho)'):
                    text_transcription=get_transcription(audio_path)
                    # text_transcription_splited=split_text(text_transcription)
                    st.text_area(label='Ler',value=text_transcription, height=100)

    
    # --------------------------------------------------------------------------
    if os.path.exists(audio_path):

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        cols = st.columns([7,1])
        cols[0].markdown('#### 5) Comece a interagir com a Genyt')

        chat = st.container(border=True, height=490)
        input_container = st.container()
        
        if cols[1].button('Limpar histórico'):
            st.session_state.messages = []
        
        chat.chat_message('assistant').write('Olá! Eu sou GenYT, sua assistente generativa para explorar o conteúdo de vídeos do Youtube.')
        chat.chat_message('assistant').write('Como posso ajudar?')

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            chat.chat_message(message["role"]).markdown(message["content"])
        
        if prompt := input_container.chat_input(placeholder='Pergunte algo para a GenYT'):

            # Display user message in chat message container
            chat.chat_message("user").write(prompt)

            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            if 'Resumo' in prompt:
                # prompt = "Listen carefully to the following audio file. Provide a brief summary."
                prompt_genai = "Escute cuidadosamente o arquivo de audio a seguir. Forneça um breve resumo."
                audio_file_genai = upload_audio_genai(audio_path, TOKEN)
                response = prompt_audio(prompt_genai, audio_file_genai).text
                chat.chat_message("assistant").markdown(response)
            elif 'Poema' in prompt:
                prompt_genai = "Escute cuidadosamente o arquivo de audio a seguir. Crie um poema sobre o conteúdo."
                audio_file_genai = upload_audio_genai(audio_path, TOKEN)
                response = prompt_audio(prompt_genai, audio_file_genai).text
                chat.chat_message("assistant").markdown(response)
            else:
                # response = f'Escutei: {prompt}'
                audio_file_genai = upload_audio_genai(audio_path, TOKEN)
                response = prompt_audio('Escute cuidadosamente o arquivo de audio. E faça o que se pede a seguir:' + prompt, audio_file_genai).text
                chat.chat_message("assistant").markdown(response)

            # Add assistant response to chat history
            if response:
                st.session_state.messages.append({"role": "assistant", "content": response})
else:
    div_info.info('Insira um URL para prosseguir!')


            
