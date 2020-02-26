from pydub import AudioSegment
t1 = 10 * 1000 #Works in milliseconds
t2 = 15 * 1000
newAudio = AudioSegment.from_wav("Abhin.wav")
newAudio = newAudio[t1:t2]
newAudio.export('newSong.wav', format="wav") #Exports to a wav file in the current path.


# last_5_seconds = newAudio[-5000:]