mysp=__import__("my-voice-analysis")
import soundfile as sf
import pyloudnorm as pyln
from threading import Thread
import math
from pydub import AudioSegment
import os, time
import speech_recognition as sr
from multiprocessing import Process, Queue
import os
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums
from google.oauth2 import service_account
from google.cloud import storage
from config import *
import random, time

credentialsPathSpeech = 'bigTalkVoice-8f1a88e93d49.json'
credentialsPathStorage = 'bigTalkVoice-a7fdfac75e5d.json'

sliceTime = 30
fillerWords = ["um", "uh", "er", "ah", "like", "okay", "right","you know"]

def getClarityMessage(clarity):
    clarity = float(clarity)
    if(clarity >= CLARITY_RANGE[0] and clarity <= CLARITY_RANGE[1]):
        return random.choice(messages["clarity"]["good"]), True
    else:
        return random.choice(messages["clarity"]["bad"]), False

def getIntonationMessage(intonation):
    intonation = float(intonation)
    if(intonation >= INTONATION_RANGE[0] and intonation <= INTONATION_RANGE[1]):
        return random.choice(messages["intonation"]["good"]), True
    else:
        return random.choice(messages["intonation"]["bad"]), False

def getLoudnessMessage(loudness):
    loudness = float(loudness)
    if(loudness >= MINIMUM_LOUDNESS):
        return random.choice(messages["loudness"]["good"]), True
    else:
        return random.choice(messages["loudness"]["bad"]), False

def getFillerWordsMessage(numberOfFillerWords, minutes):
    if(numberOfFillerWords <= numberOfFillerWords*minutes):
        return random.choice(messages["fillerWords"]["good"]), True
    else:
        return random.choice(messages["fillerWords"]["bad"]), False

def getPausesMessage(numberOfPauses, minutes):
    numberOfPauses = float(numberOfPauses)
    if(numberOfPauses <= numberOfPauses*minutes):
        return random.choice(messages["pauses"]["good"]), True
    else:
        return random.choice(messages["pauses"]["bad"]), False

def getSpeechRateMessage(speechRate):
    speechRate = float(speechRate)
    if(speechRate >= SPEECHRATE_RANGE[0] and speechRate <= SPEECHRATE_RANGE[1]):
        return random.choice(messages["speechRate"]["good"]), True
    elif(speechRate < SPEECHRATE_RANGE[0]):
        return random.choice(messages["speechRate"]["low"]), False
    else:
        return random.choice(messages["speechRate"]["high"]), False

# class ThreadWithReturnValue(Thread):
#     def __init__(self, group=None, target=None, name=None,
#                  args=(), kwargs={}, Verbose=None):
#         Thread.__init__(self, group, target, name, args, kwargs)
#         self._return = None
#     def run(self):
#         print(type(self._target))
#         if self._target is not None:
#             self._return = self._target(*self._args,
#                                                 **self._kwargs)
#     def join(self, *args):
#         Thread.join(self, *args)
#         return self._return

def deleteIfExists(fileName):
    if(os.path.isfile(fileName+'.wav')):
        os.remove(fileName+'.wav')
    if(os.path.isfile(fileName+'.TextGrid')):
        os.remove(fileName+'.TextGrid')

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

    try:
        operation = client.long_running_recognize(config, audio)
        response = operation.result()
    except Exception as e:
        raise e
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

    try:

        temp = mysp.mysptotal(p,c)
        result2 = []
        result = {}

        if(requestType == "realtime"):

            result["intonation"] = [temp["f0_std"]]
            result["loudness"] = [getLoudness(p)]
            result["clarity"] = [temp["articulation_rate"]]
            result["duration"] = [getAudioDuration(p)]
            loudness_message, result["isLoudnessGood"] = getLoudnessMessage(result["loudness"][0])
            clarity_message, result["isClarityGood"] = getClarityMessage(temp["articulation_rate"])
            intonation_message, result["isIntonationGood"] = getIntonationMessage(temp["f0_std"])
            if(result["isLoudnessGood"] == False):
                result["message"] = random.choice(messages["realTime"]["loudness"])
            elif(result["isClarityGood"] == False):
                result["message"] = random.choice(messages["realTime"]["clarity"])
            elif(result["isIntonationGood"] == False):
                result["message"] = random.choice(messages["realTime"]["intonation"])
            else:
                result["message"] = random.choice(messages["realTime"]["perfect"])
            return (result)

        if(requestType == "basic"):
            result2.append(temp["f0_std"])
            result2.append(getLoudness(p))
            result2.append(temp["articulation_rate"])
            result2.append(temp["number_of_pauses"])
            result2.append(math.ceil(int(temp["rate_of_speech"])*float(temp["original_duration"])*(60/float(temp["original_duration"]))/1.74))        

        if(requestType == "advanced"):
            result2.append(temp["f0_std"])
            result2.append(getLoudness(p))
            result2.append(temp["articulation_rate"])
            result2.append(temp["number_of_pauses"])
            result2.append(math.ceil(temp["rate_of_speech"]*float(temp["original_duration"])*(60/float(temp["original_duration"]))/1.74))
            # TODO call google API
        return (result2)

    except:
        raise ValueError("Audio was not clear")

        

def getResultRealTime(p,c):
    try:
        return (getResults(p,c,"realtime"))
    except:
        raise ValueError("Audio was not clear")

def getResultSlicedAudio(p,c,q):
    time1 = time.time()
    intonation = []
    loudness = []
    clarity = []
    pauses = []
    speechRate = []
    result = {}
    if(getAudioDuration(p)<=60):
        audioDuration = getAudioDuration(p)
    else:
        audioDuration = getAudioDuration(p)//2
    fullAudioFile = AudioSegment.from_wav(p+".wav")
    i = 0
    # import pdb; pdb.set_trace()
    while(i < math.floor(audioDuration//30)):
        temp = fullAudioFile[i*30*1000:(i*30+30)*1000]
        temp.export(p+str(i)+'.wav', format = "wav")
        try:
            data = getResults(p+str(i),c,"basic")
            intonation.append(data[0])
            loudness.append(data[1])
            clarity.append(data[2])
            pauses.append(data[3])
            speechRate.append(data[4])
        except:
            intonation.append("NA")
            loudness.append("NA")
            clarity.append("NA")
            pauses.append("NA")
            speechRate.append("NA")
        deleteIfExists(p+str(i))
        i+=1
    if(i == 0):
        q.put({})
    remainingTime = math.floor(audioDuration%30)*1000
    if(remainingTime>=15*1000):
        temp = fullAudioFile[i*30*1000:(i*30+remainingTime)*1000]
        temp.export(p+str(i)+'.wav', format = "wav")
        try:
            data = getResults(p+str(i),c,"basic")
            intonation.append(data[0])
            loudness.append(data[1])
            clarity.append(data[2])
            pauses.append(data[3])
            speechRate.append(data[4])
        except:
            intonation.append("NA")
            loudness.append("NA")
            clarity.append("NA")
            pauses.append("NA")
            speechRate.append("NA")
    deleteIfExists(p+str(i))

    result["intonation"] = intonation
    result["loudness"] = loudness
    result["clarity"] = clarity
    result["pauses"] = pauses
    result["speechRate"] = speechRate
    print("start time slice1 = ", time1)
    print("Slice1 : " ,(time.time()-time1))
    # print("slice1 : ", result)
    q.put(result)
    # return (result)
    

def getResultSlicedAudio2(p,c,q):
    time1 = time.time()
    intonation = []
    loudness = []
    clarity = []
    pauses = []
    speechRate = []
    result = {}
    audioDuration = getAudioDuration(p)
    fullAudioFile = AudioSegment.from_wav(p+".wav")
    if((audioDuration//2)%30>=15000):
        i = int((audioDuration//60)+1)
    else:
        i = int(audioDuration//60)
    while(i < math.floor(audioDuration//30)):
        temp = fullAudioFile[i*30*1000:(i*30+30)*1000]
        temp.export(p+str(i)+'.wav', format = "wav")
        try:
            data = getResults(p+str(i),c,"basic")
            intonation.append(data[0])
            loudness.append(data[1])
            clarity.append(data[2])
            pauses.append(data[3])
            speechRate.append(data[4])
        except:
            intonation.append("NA")
            loudness.append("NA")
            clarity.append("NA")
            pauses.append("NA")
            speechRate.append("NA")
        deleteIfExists(p+str(i))
        i+=1
    # if(i == 0):
    #     return {}
    remainingTime = math.floor(audioDuration%30)*1000
    if(remainingTime>=15*1000):
        temp = fullAudioFile[-remainingTime:]
        temp.export(p+str(i)+'.wav', format = "wav")
        try:
            data = getResults(p+str(i),c,"basic")
            intonation.append(data[0])
            loudness.append(data[1])
            clarity.append(data[2])
            pauses.append(data[3])
            speechRate.append(data[4])
        except:
            intonation.append("NA")
            loudness.append("NA")
            clarity.append("NA")
            pauses.append("NA")
            speechRate.append("NA")
    deleteIfExists(p+str(i))

    result["intonation"] = intonation
    result["loudness"] = loudness
    result["clarity"] = clarity
    result["pauses"] = pauses
    result["speechRate"] = speechRate
    print("start time slice2 = ", time1)
    print("Slice2 : " ,(time.time()-time1))
    # print("slice2 : ", result)
    q.put(result)
    # return (result)
    
    

def getResultFullAudio(p,c,q):
    time1 = time.time()
    intonation = []
    loudness = []
    clarity = []
    pauses = []
    speechRate = []
    result = {}
    try:
        data = getResults(p,c,"basic")
        intonation.append(data[0])
        loudness.append(data[1])
        clarity.append(data[2])
        pauses.append(data[3])
        speechRate.append(data[4])
    except:
        raise ValueError("Audio was not clear")

    
    result["intonation"] = intonation
    result["loudness"] = loudness
    result["clarity"] = clarity
    result["pauses"] = pauses
    result["speechRate"] = speechRate
    result["duration"] = getAudioDuration(p)
    print("start time full = ", time1)
    print("Full : " ,(time.time()-time1))
    q.put(result)
    # return(result)

def getResultBasic(p,c):
    try:
        q1 = Queue()
        q2 = Queue()
        audioDuration = getAudioDuration(p)
        t1 = Process(target=getResultSlicedAudio, args=(p,c,q1,))
        t2 = Process(target=getResultFullAudio, args=(p,c,q2,))
        if(audioDuration>60):
            q3 = Queue()
            t3 = Process(target=getResultSlicedAudio2, args=(p,c,q3,))
            t1.start()
            t3.start()
            t2.start()
            temp1 = q1.get()
            t1.join()
            temp2 = q2.get()
            t2.join()
            temp3 = q3.get()
            t3.join()
            temp1["clarity"].extend(temp3["clarity"])
            temp1["loudness"].extend(temp3["loudness"])
            temp1["pauses"].extend(temp3["pauses"])
            temp1["speechRate"].extend(temp3["speechRate"])
            temp1["intonation"].extend(temp3["intonation"])
            temp1["full"] = temp2
            temp1["clarity_message"],temp1["isClarityGood"] = getClarityMessage(temp2["clarity"][0])
            temp1["loudness_message"],temp1["isLoudnessGood"] = getLoudnessMessage(temp2["loudness"][0])
            temp1["intonation_message"],temp1["isIntonationGood"] = getIntonationMessage(temp2["intonation"][0])
            temp1["pauses_message"],temp1["isPausesGood"] = getPausesMessage(temp2["pauses"][0], round(temp2["duration"]/60))
            temp1["speechRate_message"],temp1["isSpeechRateGood"] = getSpeechRateMessage(temp2["speechRate"][0])
            return temp1
        else:
            t1.start()
            t2.start()
            temp1 = q1.get()
            temp2 = q2.get()
            t1.join()
            t2.join()
            temp1["full"] = temp2
            temp1["clarity_message"],temp1["isClarityGood"] = getClarityMessage(temp2["clarity"][0])
            temp1["loudness_message"],temp1["isLoudnessGood"] = getLoudnessMessage(temp2["loudness"][0])
            temp1["intonation_message"],temp1["isIntonationGood"] = getIntonationMessage(temp2["intonation"][0])
            temp1["pauses_message"],temp1["isPausesGood"] = getPausesMessage(temp2["pauses"][0], round(temp2["duration"]/60))
            temp1["speechRate_message"],temp1["isSpeechRateGood"] = getSpeechRateMessage(temp2["speechRate"][0])
            return temp1
    except:
        raise ValueError("Audio was not clear")
    

def getResultAdvanced(p,c):
    dictionary = {}
    for word in fillerWords:
        dictionary[word] = 0
    dictionary["text"] = ""
    try:
        data = callGoogle(p+'.wav')
    except Exception as e:
        raise e
    count = 0
    for word in fillerWords:
        dictionary[word] += data[word]
        count+=data[word]
    dictionary["text"] += data["text"]
    dictionary["duration"] = getAudioDuration(p)
    dictionary["fillerWords_message"],dictionary["isFillerWordsGood"] = getPausesMessage(count, round(dictionary["duration"]/60))
    # print(dictionary)
    return dictionary
