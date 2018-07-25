import json
import socket
import sys
import collections

from multiprocessing.dummy import Value, Pool as ThreadPool

import pyaes

from audio_management import AudioRecorder, AudioPlayer
from codecs_management import Coder, Decoder


CHUNK_SIZE = 4096
SHARED_SECRET = '6aa5b26a760d53a8ae1567c3508885f8'.encode()


Audio = collections.namedtuple('Audio', 'recorder, player, coder, decoder')
Audio.__new__.__defaults__ = (Coder(), Decoder())
Sockets = collections.namedtuple('Sockets', 'in_, out, timeout')
Sockets.__new__.__defaults__ = (5.0,)
Addresses = collections.namedtuple('Addresses', 'in_, out')


class AudioCommunication:
    def __init__(self, sockets, addresses, audio, shared_secret=None):
        self.sockets = sockets
        self.addresses = addresses
        self.audio = audio
        self.shared_secret = shared_secret
        self._continue = None
        self.pool = ThreadPool(2)

    def _get_excepted_received_size(self):
        # TODO
        # return self.audio.recorder.chunk_ / (self.audio.coder.width * 2)
        # return self.audio.recorder.chunk_
        return CHUNK_SIZE

    def _encrypt(self, data):
        return pyaes.AESModeOfOperationCTR(self.shared_secret).encrypt(data)

    def _decrypt(self, data):
        return pyaes.AESModeOfOperationCTR(self.shared_secret).decrypt(data)

    def _record_and_send(self):
        self.sockets.out.settimeout(self.sockets.timeout)
        while self._continue.value:
            recording = self.audio.recorder.record_chunk()
            recording = self.audio.coder.code(recording)
            if self.shared_secret:
                recording = self._encrypt(recording)
            self.sockets.out.sendto(recording, self.addresses.in_)

    def _receive_and_play(self):
        self.sockets.in_.settimeout(self.sockets.timeout)
        while self._continue.value:
            expected_received_size = self._get_excepted_received_size()
            received, address = self.sockets.in_.recvfrom(
                expected_received_size)
            if address == self.addresses.out and received:
                if self.shared_secret:
                    received = self._decrypt(received)
                recording = self.audio.decoder.decode(received)
                self.audio.player.play_chunk(recording)

    def start(self):
        self._continue = Value('b', True)
        self.pool.apply_async(self._record_and_send, [])
        self.pool.apply_async(self._receive_and_play, [])
        self.pool.close()

    def stop(self):
        self._continue.value = False
        self.pool.join()


def tuple_address(config_address):
    return (config_address['host'], config_address['port'])


def main():
    config_filename = sys.argv[1]
    with open(config_filename, 'r') as file:
        config = json.load(file)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as out_socket, \
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as in_socket, \
            AudioRecorder(chunk_=CHUNK_SIZE) as audio_recorder, \
            AudioPlayer(chunk_=CHUNK_SIZE) as audio_player:
        out_socket.bind(tuple_address(config['me']['out_socket']))
        in_socket.bind(tuple_address(config['me']['in_socket']))

        audio_communication = AudioCommunication(
            Sockets(in_socket, out_socket),
            Addresses(tuple_address(config['caller']['in_socket']),
                      tuple_address(config['caller']['out_socket'])),
            Audio(audio_recorder, audio_player),
            # SHARED_SECRET,
        )

        audio_communication.start()
        while bool(input('Press enter to stop')):
            pass
        audio_communication.stop()


if __name__ == '__main__':
    main()
