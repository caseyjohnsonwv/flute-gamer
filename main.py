import crepe
import math
import sounddevice as sd

# shutting tensorflow up
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# custom note-to-keypress converter
from games.trackmania import TrackmaniaHandler



def freq_to_note(frequency):
    notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
    note_number = round(12 * math.log2(frequency / 440) + 49)
    note = notes[(note_number - 1 ) % len(notes)]
    octave = (note_number + 8 ) // len(notes)
    return note, octave



def main():
    bitrate = 16000
    duration = 0.15 #seconds
    num_frames = int(bitrate * duration)

    # listen for audio and convert to notes
    while True:
        data = sd.rec(num_frames, bitrate, channels=1)
        sd.wait()
        time, freq, conf, activation = crepe.predict(data, bitrate, model_capacity='tiny', step_size=(duration * 1000 // 50))
        data = zip(freq, conf)
        results = []
        for dataframe in data:
            freq, conf = dataframe
            # check for frequency audible and confidence 70%
            if freq > 50 and conf > 0.7:
                results.append(freq_to_note(freq))
            else:
                results.append(None)

        # determine most dominant note in burst
        reduction = {}
        for res in results:
            if res is None:
                ct = reduction.get(None, 0)
                reduction[None] = ct + 1
            else:
                note, octave = res
                notestring = f"{note}{octave}"
                ct = reduction.get(notestring, 0)
                reduction[notestring] = ct + 1
        print(reduction)
        reduction = list(reduction.items())
        reduction.sort(key=lambda item:item[1], reverse=True)
        dominant_note = reduction[0][0]
        print(dominant_note)

        # tell trackmania to do something
        TrackmaniaHandler.interpret_note(dominant_note)



if __name__ == '__main__':
    main()
    