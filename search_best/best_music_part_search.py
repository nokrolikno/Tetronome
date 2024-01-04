import collections
import dataclasses
import os
from itertools import islice

import librosa
import numpy as np
from pydub import AudioSegment


@dataclasses.dataclass
class Beat:
    beat_time: float
    coolness: float


class SlidingWindowMixin:
    @staticmethod
    def sliding_window(iterable, n):
        "Collect data into overlapping fixed-length chunks or blocks."
        # sliding_window('ABCDEFG', 4) --> ABCD BCDE CDEF DEFG
        it = iter(iterable)
        window = collections.deque(islice(it, n - 1), maxlen=n)
        for x in it:
            window.append(x)
            yield tuple(window)


class MusicSearcher(SlidingWindowMixin):
    FRAME_SIZE = 1024
    HOP_LENGTH = 512

    def __init__(self, source: str):
        self.source = 'source/' + source
        self.is_mp3 = False
        if source.endswith('.mp3'):
            if not os.path.isdir("source/tmp"):
                os.mkdir("source/tmp")
            sound = AudioSegment.from_mp3(self.source)
            self.source = 'source/tmp/' + source[:-3] + 'wav'
            sound.export(self.source, format="wav")
            self.is_mp3 = True

        y, sr = librosa.load(self.source, sr=44100)
        self.y = y
        self.sr = sr
        self.best_parts = np.array([])
        self._bpm = 0

    def amplitude_envelope(self):
        amplitude_envelope = []
        for i in range(0, len(self.y), self.HOP_LENGTH):
            current_frame_amplitude_envelope = max(self.y[i:i + self.FRAME_SIZE])
            amplitude_envelope.append(current_frame_amplitude_envelope)
        return np.array(amplitude_envelope)

    def define_beats(self):
        bpm, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        self._bpm = bpm
        return librosa.frames_to_time(beats)

    @property
    def bpm(self):
        if self._bpm == 0:
            raise ValueError('must call define_beats or define_best_parts first')
        return self._bpm

    @bpm.setter
    def bpm(self, x):
        self._bpm = x

    def define_best_parts(self, normalize=False) -> list[Beat]:
        """
        :param normalize: Нормализовать ли крутость до числа от 0 до 1
        :return: list[tuple(time, coolness)]
        """
        ae = self.amplitude_envelope()
        frames = range(0, ae.size)
        t = librosa.frames_to_time(frames, hop_length=self.HOP_LENGTH)
        mean_arr = [0]
        n = 100
        for elems in self.sliding_window(ae, n):
            mean_arr.append(np.mean(elems))
        mean_arr.extend([0] * (n - 2))
        mean_arr = np.array(mean_arr)
        mean_arr += 1
        volume = np.power(10000, mean_arr)
        mean_vol = [0]
        n = 3
        for elems in self.sliding_window(volume, n):
            mean_vol.append(np.mean(elems))
        mean_vol.extend([0] * (n - 2))
        mean_vol = np.array(mean_vol)
        if normalize:
            mean_vol = np.abs(mean_vol / np.max(mean_vol))
        beat_score = []
        for beat_time in self.define_beats():
            beat_score.append(Beat(beat_time, np.interp(beat_time, t, mean_vol)))
        return beat_score


if __name__ == '__main__':
    source = input('source/')
    mus_searcher = MusicSearcher(source)
    print(mus_searcher.define_best_parts(normalize=True))
