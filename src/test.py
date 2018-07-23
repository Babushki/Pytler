
from audio_management import AudioRecorder, AudioPlayer
import audioop
from codecs_management import Coder, Decoder
SECONDS = 5


frames = []
frames_coded = []
with AudioRecorder() as recorder:
    for _ in range(0, int(recorder.rate/recorder.chunk * SECONDS)):
        data = recorder.record_chunk()
        frames.append(data)

coder = Coder()
for frame in frames:
    frames_coded.append(coder.code(frame))

frames_decoded = []

decoder = Decoder()
for frame in frames_coded:
    frames_decoded.append(decoder.decode(frame))

with AudioPlayer() as player:
    for frame in frames_decoded:
        player.play_chunk(frame)