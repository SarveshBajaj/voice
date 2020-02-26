#!/usr/bin/env python3
import time

import speech_recognition as sr

from os import path
AUDIO_FILE_EN = path.join(path.dirname(path.realpath(__file__)), "Sarv.wav")

# use the audio file as the audio source
r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE_EN) as source:
    audio_en = r.record(source)  # read the entire audio file

# recognize keywords using Sphinx
try:
    # print("Sphinx recognition for \"one two three\" with different sets of keywords:")
    # print(r.recognize_sphinx(audio_en, keyword_entries=[("machine",1.0)]))
    print()
    # print(r.recognize_google(audio_en,show_all=True))
    time.sleep(5)
    # print(r.recognize_google_cloud(audio_en, preferred_phrases=["machine"]))
    f = open('bigTalkVoice-8f1a88e93d49.json','r')
    # import pdb; pdb.set_trace()
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()
    print(r.recognize_google_cloud(audio_en, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, preferred_phrases=["um", "umm", "ummm","uh","uhh", "uhhh","uhms","uhmms","uhhms"]))
    # print(r.recognize_google(audio_en))
except sr.UnknownValueError:
    print("could not understand audio")
except sr.RequestError as e:
    print("error; {0}".format(e))
