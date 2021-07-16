import socket
import sys
from enum import Enum
from threading import Thread
import bottle


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


class World:
    def __init__(self):
        self.clients = []

    def xmit(self, nickname, _input):
        for client in self.clients:
            client.conn.send(f"{nickname}: {_input}".encode('ascii'))


class ChatServerThread(Thread):

    def __init__(self, world:World):
        super().__init__()

        self.world = world

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Get rid of crappy "already in use" failures.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind socket to local host and port
        try:
            s.bind((HOST, PORT))
        except socket.error as msg:
            print('Bind failed. Error Code : ' +
                  str(msg[0]) + ' Message ' + msg[1])
            sys.exit(1)
        print("Listening to " + str(PORT))

        #Start listening on socket
        s.listen(1)

        # Master Loop
        while(True):
            print("Waiting to accept")
            conn, addr = s.accept()

            new_client = ChatClientThread(conn, addr, self.world)
            new_client.start()

            self.world.clients.append(new_client)


class ChatClientThread(Thread):

    def __init__(self, conn, addr, world):
        super().__init__()

        self.conn = conn
        self.addr = addr
        self.world = world
        self.nickname = ''

        self.inputs = []

    def publish(self):
        """Return a jsonable dict of information about this object.
        """

        return dict(addr=f"{self.addr[0]}:{self.addr[1]}",
                    nickname=self.nickname,
                    inputs=self.inputs)

    def run(self):
        print(f"Got a connection from {self.addr}")

        self.conn.send(GREETING)

        # Request Nickname
        self.conn.send(NICK)
        self.nickname = self.conn.recv(MAX_NICKNAME_LENGTH
                                       ).decode('ascii').strip()

        print(f"Got connection from {self.nickname}")
        self.conn.send(f"Hello {self.nickname}".encode('ascii'))

        # read/distribute client loop
        while True:
            _input = self.conn.recv(1024).decode('ascii').strip()
            self.world.xmit(self.nickname, _input)
            self.inputs.append(_input)

class Program:

    app = bottle.Bottle()
    world = World()

    def __init__(self):
        self.chat_server_thread = ChatServerThread(Program.world)

    def run(self):
        print("Starting Chat Server Thread")
        self.chat_server_thread.start()

        print("Running BottleApp")
        bottle.run(self.app, host='0.0.0.0', port=8080)


@Program.app.get('/index.html')
def get_app():
    return bottle.static_file("app.html",
                              root="/home/ivan/git/obearz-chat",
                              mimetype='text/html')

@Program.app.get('/world')
def get_world():
    # https://stackoverflow.com/a/12294213
    #
    # "Bottle's JSON plugin expects only dicts to be returned - not
    # arrays. There are vulnerabilities associated with returning JSON arrays
    # ..."
    #
    return {c.nickname: c.publish() for c in Program.world.clients}


if __name__ == "__main__":
    _p = Program()
    _p.run()
