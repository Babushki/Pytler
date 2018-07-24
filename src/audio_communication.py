import json
import socket
import sys
import time

from multiprocessing.dummy import Value, Pool as ThreadPool

from audio_management import AudioRecorder, AudioPlayer
from codecs_management import Coder, Decoder


CHUNK_SIZE = 4096


def record_and_send(out_socket, receiver, audio_recorder, connected):
    out_socket.settimeout(1.0)
    while connected.value:
        recording = audio_recorder.record_chunk()
        coded_recording = Coder().code(recording)
        out_socket.sendto(coded_recording, receiver)


def receive_and_play(in_socket, sender, audio_player, connected):
    in_socket.settimeout(1.0)
    while connected.value:
        received, address = in_socket.recvfrom(CHUNK_SIZE)
        if address == sender and received:
            recording = Decoder().decode(received)
            audio_player.play_chunk(recording)


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

        connected = Value('b', True)
        pool = ThreadPool(2)
        pool.apply_async(record_and_send, [
            out_socket,
            tuple_address(config['caller']['in_socket']),
            audio_recorder,
            connected,
        ])
        pool.apply_async(receive_and_play, [
            in_socket,
            tuple_address(config['caller']['out_socket']),
            audio_player,
            connected,
        ])
        pool.close()

        while bool(input('Press enter to stop')):
            pass

        connected.value = False
        pool.join()


if __name__ == '__main__':
    main()
