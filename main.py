import crepe
import math
from pynput.keyboard import Key, Controller
import sounddevice as sd

# shutting tensorflow up
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'



def freq_to_note(frequency):
    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    note_number = round(12 * math.log2(frequency / 440) + 49)
    note = notes[(note_number - 1 ) % len(notes)]
    octave = (note_number + 8 ) // len(notes)
    return note, octave



def main():
    # give python control of my keyboard
    keyboard = Controller()

    bitrate = 44100
    duration = 0.2 # seconds
    num_frames = int(bitrate * duration)
    while True:
        data = sd.rec(num_frames, bitrate, channels=1)
        sd.wait()
        time, freq, conf, activation = crepe.predict(data, bitrate, model_capacity='tiny', step_size=(duration * 1000 // 10))
        data = zip(freq, conf)
        results = []
        for dataframe in data:
            freq, conf = dataframe
            # check for frequency audible and confidence 80%
            if freq > 50 and conf > 0.8:
                results.append(freq_to_note(freq))
        results = list(set(results))
        for note, octave in results:
            print(f"{note}{octave}")
            # sing an F3 into the microphone to kill the terminal
            if note == 'F' and octave == 3:
                with(keyboard.pressed(Key.ctrl_l)):
                    keyboard.tap('c')



if __name__ == '__main__':
    main()
    