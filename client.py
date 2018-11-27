# Client Code
import socket
from common import *
from datetime import datetime


class NTPeeClient():
    def __init__(self, dest_ip, dest_port):
        self.hostport = (dest_ip, dest_port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def get_new_time(self):
        # will do a round trip request/response
        # and return the new time to sync to. Return None
        # on an error
        cr = ClientRequest(datetime.now().timestamp())
        data = cr.encode()
        try:
            self.client.sendto(data, self.hostport)
        except:
            print("error: Could send request to remote server at {}".format(
                self.hostport))
            return None
        try:
            (new_data, _) = self.client.recvfrom(24)
        except:
            print("error: Could not recv data from remote server at {}".format(
                self.hostport))
        sr = ServerResponse()
        sr.decode(new_data)
        return sr


def main():
    # open a client
    # poll every 30 seconds
    # get new time to sync to
    # apply either instant time jump or gradual time slewing
    t1 = datetime.now().timestamp()
    cr = ClientRequest(t1)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(cr.encode(), ('localhost', 9999))
    (data, peer_addr) = sock.recvfrom(24)
    print("Recv'd {} from {}".format(data.hex(), peer_addr))
    sr = ServerResponse()
    sr.decode(data)
    if sr.t1 == t1:
        print("T1 matches")
    print("T3: {}".format(sr.t3))


if __name__ == "__main__":
    main()
