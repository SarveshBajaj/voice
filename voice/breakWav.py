from pydub import AudioSegment
t1 = 0 * 1000 #Works in milliseconds
t2 = 59 * 1000
t3 = 118 * 1000
t4 = 143 * 1000
fullAudio = AudioSegment.from_wav("vjsnews.wav")
newAudio = fullAudio[t1:t2]
newAudio.export('vjsnews1.wav', format="wav") #Exports to a wav file in the current path.
newAudio = fullAudio[t2:t3]
newAudio.export('vjsnews2.wav', format="wav") #Exports to a wav file in the current path.
newAudio = fullAudio[t3:t4]
newAudio.export('vjsnews3.wav', format="wav") #Exports to a wav file in the current path.


# last_5_seconds = newAudio[-5000:]