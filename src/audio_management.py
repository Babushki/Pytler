import pyaudio

class AudioRecorder:

    def __init__(self, channels_=2, format_=pyaudio.paInt16, rate_=44100, chunk_=256):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=format_, channels=channels_,
                                 rate=rate_, input=True, frames_per_buffer=chunk_)
        self.channels = channels_
        self.format = format_
        self.rate = rate_
        self.chunk = chunk_

    def record_chunk(self):
        return self.stream.read(self.chunk)

    def __enter__(self):
        return self

    def __exit__(self, *arg):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()


class AudioPlayer:
    def __init__(self, channels_=2, format_=pyaudio.paInt16, rate_=44100, chunk_=256):
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=format_, channels=channels_,
                                    rate=rate_, output=True)
        self.channels = channels_
        self.format = format_
        self.rate = rate_
        self.chunk = chunk_

    def play_chunk(self, chunk):
        self.stream.write(chunk)

    def __enter__(self):
        return self

    def __exit__(self, *arg):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()