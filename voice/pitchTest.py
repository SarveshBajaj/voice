import amfm_decompy.basic_tools as basic
import amfm_decompy.pYAAPT as pYAAPT
import matplotlib.pyplot as plt
import numpy as np 
from aubio import sys

# load audio
signal = basic.SignalObj('Abhin.wav')
# filename = 'Abin.wav'# YAAPT pitches 
pitchY = pYAAPT.yaapt(signal, frame_length=40, tda_frame_length=40, f0_min=75, f0_max=600)

fig, (ax2) = plt.subplots(1, 1, sharex=True, sharey=True, figsize=(12, 8))
ax2.plot(pitchY.samp_values, label='YAAPT', color='blue')
ax2.legend(loc="upper right")
