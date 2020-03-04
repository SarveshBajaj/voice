mysp=__import__("my-voice-analysis")
import soundfile as sf
import pyloudnorm as pyln
from threading import Thread
import math
from pydub import AudioSegment
import os, time
import speech_recognition as sr
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums
from google.oauth2 import service_account
from google.cloud import storage

credentialsPathSpeech = 'bigTalkVoice-8f1a88e93d49.json'
credentialsPathStorage = 'bigTalkVoice-a7fdfac75e5d.json'

sliceTime = 30
fillerWords = ["um", "uh", "er", "ah", "like", "okay", "right","you know"]

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def deleteIfExists(fileName):
    if(os.path.isfile(fileName)):
        os.remove(fileName)

def callGoogle(filePath):
    # import pdb; pdb.set_trace()
    # f = open(credentialsPathSpeech,'r')
    # GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()
    

    GOOGLE_CLOUD_SPEECH_CREDENTIALS = service_account.Credentials.from_service_account_file(credentialsPathSpeech)
    client = speech_v1p1beta1.SpeechClient(credentials = GOOGLE_CLOUD_SPEECH_CREDENTIALS)

    storage_client = storage.Client.from_service_account_json(credentialsPathStorage)
    buckets = list(storage_client.list_buckets())
    bucket_name = "bigtalkaudio"
    bucket = storage_client.get_bucket(bucket_name)
    if(bucket is None):
        bucket = storage_client.create_bucket(bucket_name)

    source_file_name = filePath
    destination_blob_name = filePath
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    blob.make_public()
    URL = blob.public_url

    URL = "gs://"+bucket_name+"/"+filePath

    boost = 8.0
    speech_contexts_element = {"phrases": fillerWords, "boost": boost}
    speech_contexts = [speech_contexts_element]

    sample_rate_hertz = 44100
    language_code = "en-US"
    encoding = enums.RecognitionConfig.AudioEncoding.MP3
    config = {
        "speech_contexts": speech_contexts,
        "sample_rate_hertz": sample_rate_hertz,
        "language_code": language_code,
        "encoding": encoding,
    }
    audio = {"uri": URL}


    operation = client.long_running_recognize(config, audio)
    response = operation.result()
    blob.delete()
    text = ""
    for result in response.results:
        alternative = result.alternatives[0]
        text += alternative.transcript
    result = {}
    words = text.split(' ')
    for word in fillerWords:
        result[word] = 0
    for word in words:
        if word in fillerWords:
            result[word] += 1
    result["text"] = text
    # print(result)
    return result


def getAudioDuration(p):
    f = sf.SoundFile(p+".wav")
    return(len(f) / f.samplerate)

def getLoudness(p):
    # import pdb; pdb.set_trace()
    data, rate = sf.read(p+".wav") 
    meter = pyln.Meter(rate) 
    return (meter.integrated_loudness(data))

def getResults(p,c, requestType):

    temp = mysp.mysptotal(p,c)
    result2 = []
    result = {}

    if(requestType == "realtime"):

        result["intonation"] = [temp["f0_std"]]
        result["loudness"] = [getLoudness(p)]
        result["clarity"] = [temp["articulation_rate"]]
        return (result)

    if(requestType == "basic"):
        result2.append(temp["f0_std"])
        result2.append(getLoudness(p))
        result2.append(temp["articulation_rate"])
        result2.append(temp["number_of_pauses"])
        # import pdb; pdb.set_trace()
        result2.append(math.ceil(int(temp["rate_of_speech"])*float(temp["original_duration"])*(60/float(temp["original_duration"]))/1.74))        

    if(requestType == "advanced"):
        result2.append(temp["f0_std"])
        result2.append(getLoudness(p))
        result2.append(temp["articulation_rate"])
        result2.append(temp["number_of_pauses"])
        result2.append(math.ceil(temp["rate_of_speech"]*float(temp["original_duration"])*(60/float(temp["original_duration"]))/1.74))
        # TODO call google API

    return (result2)
        

def getResultRealTime(p,c):
    return (getResults(p,c,"realtime"))

def getResultSlicedAudio(p,c):
    intonation = []
    loudness = []
    clarity = []
    pauses = []
    speechRate = []
    result = {}
    audioDuration = getAudioDuration(p)
    fullAudioFile = AudioSegment.from_wav(p+".wav")
    i=0
    # import pdb; pdb.set_trace()
    while(i < math.floor(audioDuration//30)):
        temp = fullAudioFile[i*30*1000:(i*30+30)*1000]
        temp.export(p+str(i)+'.wav', format = "wav")
        data = getResults(p+str(i),c,"basic")
        intonation.append(data[0])
        loudness.append(data[1])
        clarity.append(data[2])
        pauses.append(data[3])
        speechRate.append(data[4])
        i+=1
        deleteIfExists(p+str(i)+'.wav')
    if(i == 0):
        return {}
    remainingTime = math.floor(audioDuration%30)*1000
    temp = fullAudioFile[-remainingTime:]
    temp.export(p+str(i)+'.wav', format = "wav")
    data = getResults(p+str(i),c,"basic")
    intonation.append(data[0])
    loudness.append(data[1])
    clarity.append(data[2])
    pauses.append(data[3])
    speechRate.append(data[4])
    deleteIfExists(p+str(i)+'.wav')

    result["intonation"] = intonation
    result["loudness"] = loudness
    result["clarity"] = clarity
    result["pauses"] = pauses
    result["speechRate"] = speechRate

    return (result)
    

def getResultFullAudio(p,c):
    intonation = []
    loudness = []
    clarity = []
    pauses = []
    speechRate = []
    result = {}

    data = getResults(p,c,"basic")
    intonation.append(data[0])
    loudness.append(data[1])
    clarity.append(data[2])
    pauses.append(data[3])
    speechRate.append(data[4])
    
    result["intonation"] = intonation
    result["loudness"] = loudness
    result["clarity"] = clarity
    result["pauses"] = pauses
    result["speechRate"] = speechRate

    return(result)

def getResultBasic(p,c):
    t1 = ThreadWithReturnValue(target=getResultSlicedAudio, args=(p,c,))
    t2 = ThreadWithReturnValue(target=getResultFullAudio, args=(p,c,))
    t1.start()
    t2.start()
    temp1 = t1.join()
    temp2 = t2.join()
    temp1["full"] = temp2
    return temp1

def getResultAdvanced(p,c):
    dictionary = {}
    for word in fillerWords:
        dictionary[word] = 0
    dictionary["text"] = ""
    data = callGoogle(p+'.wav')
    for word in fillerWords:
        dictionary[word] += data[word]
    dictionary["text"] += data["text"]
    # print(dictionary)
    return dictionary
    


   

