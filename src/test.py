
from audio_management import AudioRecorder, AudioPlayer

SECONDS = 5
with AudioRecorder() as recorder:
    with AudioPlayer() as player:
        for _ in range(0, int(recorder.rate/recorder.chunk * SECONDS)):
            data = recorder.record_chunk()
            player.play_chunk(data)