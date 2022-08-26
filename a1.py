import streamlit as st
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import nltk
from nltk.corpus import stopwords
import pandas as pd
nltk.download('stopwords')
nltk.download('punkt')
from nltk.tokenize import word_tokenize
from word2number import w2n
import speech_recognition as sr

st.title(""" Order Placement """)

z = '1.wav'
st.subheader("Sample Audio to try the app")
st.audio(z)

f = st.file_uploader('Upload a audio file (wav format')

if f is not None:
    if f.name.endswith('.wav'):
        r = sr.Recognizer()

        def get_large_audio_transcription(path):
            """
            Splitting the large audio file into chunks
            and apply speech recognition on each of these chunks
            """
            sound = AudioSegment.from_wav(path)
            chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=sound.dBFS - 14, keep_silence=500)
            folder_name = "audio-chunks"
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            whole_text = ""
            for i, audio_chunk in enumerate(chunks, start=1):
                chunk_filename = os.path.join(folder_name, f"{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                with sr.AudioFile(chunk_filename) as source:
                    audio_listened = r.record(source)
                    try:
                        text = r.recognize_google(audio_listened)
                    except sr.UnknownValueError as e:
                        print("Error:", str(e))
                    else:
                        text = f"{text.capitalize()}. "
                        print(chunk_filename, ":", text)
                        whole_text += text
            return whole_text


        def transcription_tokens(audio):
            x = get_large_audio_transcription(audio)
            text_tokens = word_tokenize(x)
            print(text_tokens)
            return text_tokens


        remove_words = ['.', '..', '~', "`", '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '=', '{',
                        '}',
                        '[', ']', '|',
                        ':', ';', '/', '?', '>', '<', ',']
        pronouns = ['he', 'him', 'her', 'it', 'me', 'she', 'them', 'they', 'us', 'we', 'you']
        modal_verbs = ['will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must', 'dare', 'need',
                       'ought']
        flavor = ['original', 'vanilla', 'cherry', ' cherry vanilla', 'original zero sugar', 'vanilla zero sugar',
                  'cherry zero sugar', 'cherry vanilla zero sugar']
        packaging_type = ['box', 'boxes', 'case', 'cases', 'carton', 'cartons', 'pack', 'packs']
        beverage_container = ['can', 'cans', 'bottle', 'bottles']

        a = transcription_tokens(f)
        tokens = [word for word in a if not word in remove_words]
        print(tokens)
        a = tokens
        f = None
        size = None
        b = None
        qty = None
        # NUMERIC WORD TO INTEGER
        for i in range(len(a)):
            try:
                if a[i].lower() != 'zero':
                    x = w2n.word_to_num(a[i])
                    a[i] = str(x)
                if a[i] == 'l.':
                    a[i] = 'L'
                if a[i].lower() == 'dozen':
                    a[i] = '12'
            except:
                if a[i] == 'l.':
                    a[i] = 'L'
                if a[i].lower() == 'dozen':
                    a[i] = '12'
        print("Order: ", a)
        print(" ")

        for i in range(len(a)):
            # FLAVORS
            if i and i + 1 and i + 2 and i + 3 < len(a):
                if a[i].lower() + ' ' + a[i + 1].lower() + ' ' + a[i + 2].lower() + ' ' + a[i + 3].lower() in flavor:
                    f = (a[i] + ' ' + a[i + 1] + ' ' + a[i + 2] + ' ' + a[i + 3])
                    # st.write('Flavor:', f)
                    # st.markdown("**Flavor :**")
                    # st.write(f)
                    continue
            if i and i + 1 and i + 2 < len(a):
                if a[i].lower() + ' ' + a[i + 1].lower() + ' ' + a[i + 2].lower() in flavor:
                    f = (a[i] + ' ' + a[i + 1] + ' ' + a[i + 2])
                    # st.markdown("**Flavor :**")
                    # st.write(f)
                    continue
            if i and i + 1 < len(a):
                if a[i].lower() + ' ' + a[i + 1].lower() in flavor:
                    f = (a[i] + ' ' + a[i + 1])
                    # st.markdown("**Flavor :**")
                    # st.write(f)
                    continue
            if i <= len(a):
                if a[i].lower() in flavor:
                    f = a[i]
                    # st.markdown("**Flavor :**")
                    # st.write(f)
                    continue

            # size
            if a[i] == 'oz' or a[i] == 'L' or a[i] == 'liter':
                if a[i - 1].isdigit() == True:
                    size = a[i - 1] + ' '+a[i]
                    # st.markdown("**Size :**")
                    # st.write(size)

            # Beverage Container
            if a[i] in beverage_container:
                if i + 1 <= len(a) - 1:
                    if a[i + 1] not in pronouns:
                        b = a[i]
                        # st.write('Beverage Container: ', b)
                if i == len(a) - 1:
                    b = a[i]
                    # st.write('Beverage Container: ', b)

            # Packaging type and quantity
            if a[i] in packaging_type:
                if a[i - 1].isdigit():
                    qty = a[i - 1] + ' ' + a[i]
                    # st.write('Package Quantity and Type: ', qty)
                else:
                    qty = '1' + ' ' + a[i]
                    # st.write('Package Quantity and Type: ', qty)

        cnt = 0
        ecnt = 0
        st.write(" ")

        st.subheader("Fetched Data")
        l1 = []
        l2 = []
        cnt = 0
        ncnt = 0
        if f is not None:
            cnt = cnt + 1
        if b is not None:
            cnt = cnt + 1
        if size is not None:
            cnt = cnt + 1
        if qty is not None:
            cnt = cnt + 1

        if f is None:
            ncnt = ncnt + 1
        if b is None:
            ncnt = ncnt + 1
        if size is None:
            ncnt = ncnt + 1
        if qty is None:
            ncnt = ncnt + 1

        l1 = []
        l1.append(['Beverage Flavor', f])
        l1.append(['Beverage Container Type', b])
        l1.append(['Beverage Container Size', size])
        l1.append(['Package Quantity and Type', qty])

        df = pd.DataFrame(l1).T
        df.columns = df.iloc[0]
        df = df.drop(index=0)

        if cnt == 4:
            st.write("All data available")
            st.dataframe(df)
        elif cnt == 0:
            st.write("No data available")
            st.dataframe(df)
        else:
            st.write(cnt, " / 4 required data available")
            st.dataframe(df)

        #st.dataframe(df)


