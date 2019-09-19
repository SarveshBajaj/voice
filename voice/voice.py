#pip install my-voice-analysis
#pip install Speech_recognition or #pip install SpeechRecognition
import speech_recognition as sr
import sys, time
mysp=__import__("my-voice-analysis")
#p= "Abhinav"
#c=r"C:\Users\soura\Desktop\Projects_iNeuron.ai\Voice Analysis"
@profile
def write_to_txtfile(p,c):
    sys.stdout = open(without_wav+'.txt','wt')
    # mysp.myspgend(p,c)
    # mysp.mysppron(p,c)
    # mysp.myspsyl(p,c)
    # mysp.mysppaus(p,c)
    # mysp.myspsr(p,c)
    # mysp.myspatc(p,c)
    # mysp.myspst(p,c)
    # mysp.myspod(p,c)
    # mysp.myspbala(p,c)
    # mysp.myspf0mean(p,c)
    # mysp.myspf0mean(p,c)
    # mysp.myspf0sd(p,c)
    # mysp.myspf0med(p,c)
    dict = mysp.mysptotal(p,c)
    print()
    for key in dict:
        print(key," = ", dict[key])
    print()
    return None

@profile
def speech_to_text(t):
    start = time.time()
    r = sr.Recognizer()
    with sr.AudioFile(t) as source:
        audio = r.record(source)
    try:
        z = r.recognize_google(audio)
        print("Time taken for speech to text: ",time.time() - start,"\n")
        print("Text: "+z)
        print()
    except Exception as y:
        print("Exception: "+str(y))



def speech_to_text_write(with_wav, without_wav):
    sys.stdout = open(without_wav+'.txt','a+')
    speech_to_text(with_wav)
    return None

import glob
for filename in glob.glob('*.wav'):
    with_wav = str(filename)
    without_wav = with_wav.replace(".wav","")
    #print(with_wav)
    #print(without_wav)

    #output_1 = voice_analysis(p = without_wav, c=r"C:\Users\soura\Desktop\Projects_iNeuron.ai\Voice Analysis")
    #output_2 = speech_to_text(t=with_wav)

    write_to_txtfile(without_wav,'/home/sarvesh/Downloads/HappyMongo/voice/')
    # speech_to_text_write(with_wav, without_wav)
