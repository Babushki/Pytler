import datetime
import json
import socket
import sys
import time

from multiprocessing.dummy import Pool as ThreadPool

CHUNK_SIZE = 1024
SLEEP_SECONDS = 1


def send(out_socket, receiver):
    while True:
        message = '{:%F %T}'.format(datetime.datetime.now()).encode()
        out_socket.sendto(message, receiver)
        print('Sent {!r}'.format(message))
        time.sleep(SLEEP_SECONDS)


def receive(in_socket, sender):
    while True:
        received, address = in_socket.recvfrom(CHUNK_SIZE)
        if address == sender:
            print('Received {!r} from {}'.format(received.decode(), address))
        else:
            print('Message from invalid sender')
        time.sleep(SLEEP_SECONDS)


def tuple_address(config_address):
    return (config_address['host'], config_address['port'])

def main():
    config_filename = sys.argv[1]
    with open(config_filename, 'r') as file:
        config = json.load(file)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as out_socket, \
         socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as in_socket:
        out_socket.bind(tuple_address(config['me']['out_socket']))
        in_socket.bind(tuple_address(config['me']['in_socket']))

        pool = ThreadPool(2)
        pool.apply_async(send, [out_socket, tuple_address(config['caller']['in_socket'])])
        pool.apply_async(receive, [in_socket, tuple_address(config['caller']['out_socket'])])
        pool.close()
        time.sleep(10)
        pool.terminate()

if __name__ == '__main__':
    main()
