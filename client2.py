# Client Code
import socket
from common import *
from datetime import datetime
import sys
import time
import os

# poll times in seconds
MIN_POLL = 4.0

STEP_THRESHOLD = 128  # milliseconds

TICK_MAX = 11000
TICK_MIN = 9000


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


def calc_offset(t1, t2, t3, t4):
    return ((t2 - t1) + (t3 - t4)) / 2


def calc_delay(t1, t2, t3, t4):
    return ((t4 - t1) - (t3 - t2)) / 2


def calc_newtime(t1, t2, t3, t4):
    offset = calc_offset(t1, t2, t3, t4)
    return datetime.now().timestamp() + offset


def main():
    # open a client
    # poll every 30 seconds
    # get new time to sync to
    # apply either instant time jump or gradual time slewing
    polltime = MIN_POLL
    hostip = socket.gethostbyname(sys.argv[1])
    hostport = (hostip, 9999)
    print("Connecting to {}".format(hostport))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:
        t1 = datetime.now().timestamp()
        cr = ClientRequest(t1)
        sock.sendto(cr.encode(), hostport)
        (data, peer_addr) = sock.recvfrom(24)
        print("Recv'd {} from {}".format(data.hex(), peer_addr))
        t4 = datetime.now().timestamp()
        sr = ServerResponse()
        sr.decode(data)
        if sr.t1 == t1:
            print("T1 matches")
        t2 = sr.t2
        t3 = sr.t3
        offset = calc_offset(t1, t2, t3, t4)
        print("T3: {}".format(datetime.fromtimestamp(t3)))
        print("T4: {}".format(datetime.fromtimestamp(t4)))
        print("Offset: {:.2f}ms".format(offset*1000))
        print("Delay: {:.2f}ms".format(calc_delay(t1, t2, t3, t4)*1000))
        tick_factor = choose_factor(offset*1000)  # turn to ms
        print("Tick factor: {}".format(tick_factor))
        time.sleep(MIN_POLL)
        # DayOfWeek Year-Month-Day HH:MM:SEC.MS TIMEZONE


def choose_factor(offset):
    if offset == 0:
        return 10000
    if offset > 1000:
        return 11000
    elif offset > 0:
        return 10010
    elif offset > -1000:
        return 9995
    else:
        return 9000


if __name__ == "__main__":
    main()
