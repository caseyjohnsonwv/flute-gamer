import crepe
import math
from pynput.keyboard import Key, Controller
import sounddevice as sd

# shutting tensorflow up
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'



def freq_to_note(frequency, confidence):
    try:
        if confidence * 100 < 80:
            # force value error
            math.log2(0)
        notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        note_number = round(12 * math.log2(frequency / 440) + 49)
        note = notes[(note_number - 1 ) % len(notes)]
        octave = (note_number + 8 ) // len(notes)
    except ValueError:
        note = None
        octave = -math.inf
    return note, octave



def main():
    # give python control of my keyboard
    keyboard = Controller()

    bitrate = 44100
    duration = 0.1 # seconds
    num_frames = int(bitrate * duration)
    while True:
        data = sd.rec(num_frames, bitrate, channels=1)
        sd.wait()
        time, freq, conf, activation = crepe.predict(data, bitrate, model_capacity='tiny', step_size=(duration * 1000 // 2))
        data = zip(freq, conf)
        results = [freq_to_note(frequency = dataframe[0], confidence = dataframe[1]) for dataframe in data]
        for note, octave in results:
            if note is not None:
                print(f"{note}{octave}")
                # sing an F3 into the microphone to kill the terminal
                if note == 'F' and octave == 3:
                    with(keyboard.pressed(Key.ctrl_l)):
                        keyboard.tap('c')



if __name__ == '__main__':
    main()
    