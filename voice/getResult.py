mysp=__import__("my-voice-analysis")
import soundfile as sf
import pyloudnorm as pyln
from threading import Thread
import math
from pydub import AudioSegment
import os, time

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

def getAudioDuration(p):
    f = sf.SoundFile(p+".wav")
    return(len(f) / f.samplerate)

def getLoudness(p):
    # import pdb; pdb.set_trace()
    data, rate = sf.read(p+".wav") 
    meter = pyln.Meter(rate) 
    return (meter.integrated_loudness(data))

def getResults(p,c, requestType):

    temp = {}
    result2 = []
    result = {}

    if(requestType == "realtime"):
        p+='/RealTime'
        temp = mysp.mysptotal(p,c)
        result["intonation"] = [temp["f0_std"]]
        result["loudness"] = [getLoudness(p)]
        result["clarity"] = [temp["articulation_rate"]]
        return (result)

    if(requestType == "basic"):
        p+='/Basic'
        temp = mysp.mysptotal(p,c)
        result2.append(temp["f0_std"])
        result2.append(getLoudness(p))
        result2.append(temp["articulation_rate"])
        result2.append(temp["number_of_pauses"])
        # import pdb; pdb.set_trace()
        result2.append(math.ceil(int(temp["rate_of_speech"])*float(temp["original_duration"])/1.74))        

    if(requestType == "advanced"):
        result2.append(temp["f0_std"])
        result2.append(getLoudness(p))
        result2.append(temp["articulation_rate"])
        result2.append(temp["number_of_pauses"])
        result2.append(math.ceil(temp["rate_of_speech"]*temp["original_duration"]/1.74))
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
    for i in range(math.floor(audioDuration//30)):
        temp = fullAudioFile[i*30*1000:(i*30+30)*1000]
        temp.export(str(i)+'.wav', format = "wav")
        data = getResults(str(i),c,"basic")
        intonation.append(data[0])
        loudness.append(data[1])
        clarity.append(data[2])
        pauses.append(data[3])
        speechRate.append(data[4])
    
    remainingTime = math.floor(audioDuration%30)*1000
    temp = fullAudioFile[-remainingTime:]
    temp.export(str(i)+'.wav', format = "wav")
    data = getResults(str(i),c,"basic")
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


# p = "vjsnews"
# c = os.path.dirname(os.path.realpath(__file__))
# start = time.time()
# print(getResultRealTime(p,c))
# print()
# getResultBasic(p,c)
# print(time.time()-start)

   
