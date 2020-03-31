# from google.cloud import speech_v1p1beta1
# from google.cloud.speech_v1p1beta1 import enums
# import io


# def sample_recognize(local_file_path):

#     client = speech_v1p1beta1.SpeechClient()

#     # storage_uri = 'gs://cloud-samples-data/speech/brooklyn_bridge.mp3'
#     # phrase = 'Brooklyn Bridge'
#     phrases = ["um", "uh", "er", "ah", "like", "okay", "right","you know"]

#     # Hint Boost. This value increases the probability that a specific
#     # phrase will be recognized over other similar sounding phrases.
#     # The higher the boost, the higher the chance of false positive
#     # recognition as well. Can accept wide range of positive values.
#     # Most use cases are best served with values between 0 and 20.
#     # Using a binary search happroach may help you find the optimal value.
#     boost = 10.0
#     speech_contexts_element = {"phrases": phrases, "boost": boost}
#     speech_contexts = [speech_contexts_element]

#     # Sample rate in Hertz of the audio data sent
#     sample_rate_hertz = 44100

#     # The language of the supplied audio
#     language_code = "en-US"

#     # Encoding of audio data sent. This sample sets this explicitly.
#     # This field is optional for FLAC and WAV audio formats.
#     encoding = enums.RecognitionConfig.AudioEncoding.MP3
#     config = {
#         "speech_contexts": speech_contexts,
#         "sample_rate_hertz": sample_rate_hertz,
#         "language_code": language_code,
#         "encoding": encoding,
#     }
#     with io.open(local_file_path, "rb") as f:
#         content = f.read()
#     audio = {"content": content}

#     operation = client.recognize(config, audio)
#     print(u"Waiting for operation to complete...")
#     response = operation.result()

#     for result in response.results:
#         # First alternative is the most probable result
#         alternative = result.alternatives[0]
#         print(u"Transcript: {}".format(alternative.transcript))

# sample_recognize("vjsnews1.wav")
# print()
# sample_recognize("vjsnews2.wav")
# print()
# sample_recognize("vjsnews3.wav")
# print()
# sample_recognize("vjsnews4.wav")


















import speech_recognition as sr

from os import path
import time

listed = ["vjsnews1.wav","vjsnews2.wav","vjsnews3.wav"]

for i in listed:

    AUDIO_FILE_EN = path.join(path.dirname(path.realpath(__file__)), i)

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
        print(r.recognize_google_cloud(audio_en, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS, preferred_phrases=["um", "umm", "ummm","uh","uhh","uhhh","uhms","uhmms","uhhms","huh"]))
        # print(r.recognize_google(audio_en))
    except sr.UnknownValueError:
        print("could not understand audio")
    except sr.RequestError as e:
        print("error; {0}".format(e))

