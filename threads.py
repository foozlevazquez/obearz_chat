import time
import socket
import sys
from enum import Enum
from threading import Thread

logfilename = '/tmp/listener.log'
HOST = ''   # Symbolic name, meaning all available interfaces
PORT = 9876 # Arbitrary non-privileged port


MAX_NICKNAME_LENGTH = 128

# Define the protocol
GREETING = "Howza".encode('ascii')
NICK = "nick".encode('ascii')
LIST = "list".encode('ascii')
EXIT = "exit".encode('ascii')
MYSPECIALTHING = 'foobarbaz'.encode('ascii')


class Server:

    def __init__(self):
        self.clients = []

    def run(self):

        # Master Loop
        for i in range(10):
            new_client = ClientThread(i)
            time.sleep(1)
            new_client.start()
            self.clients.append(new_client)

        time.sleep(10)
        sys.exit(0)


class ClientThread(Thread):

    def __init__(self, n):
        super().__init__()

        self.n = n

    def run(self):
        print(f"THREAD [{self.n}] starting")
        i = 0

        while True:
            print(f"THREAD [{self.n}] at i={i}")
            time.sleep(0.25)
            i += 1



if __name__ == "__main__":
    server = Server()

    server.run()
