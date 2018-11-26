# Common code
import enum
import abc
import struct

DEBUG = True


def debug_print(msg):
    if DEBUG:
        print(msg)


class Message(metaclass=abc.ABCMeta):
    """
    Abstract base class for all MessageTypes.
    Each message should know how to encode itself
    to a byte array, and decode a byte array and
    update itself.
    """

    @abc.abstractmethod
    def encode(self):
        """
        Should encode all values and return a byte array.
        Should not worry about encoding the MsgType id or 
        the msg len value. That will be handle elsewhere.
        """

    @abc.abstractmethod
    def decode(self, data):
        """
        Should decode the given data byte array
        and set the appropriate member variables.
        Should not worry about decoding the MsgType id or 
        the msg len value from data, those will be stripped off.
        """


class ClientRequest(Message):
    """
    ClientRequest is sent between a NTP client and server
    recording t1. Server will send a ServerResponse containing
    t2 and t3. All timestamps are 64 bit unix timestamps (doubles)
    """

    def __init__(self, t1=None):
        self.t1 = t1

    def encode(self):
        frame = bytearray()
        frame.extend(struct.pack(">d", self.t1))
        return frame

    def decode(self, data):
        self.t1 = struct.unpack(">d",  data)[0]


class ServerResponse(Message):
    """
    ServerResponse is sent between from a NTP server
    to client recording t1, t2, t3 in resonse to ClientRequest
    """

    def __init__(self, t1=None, t2=None, t3=None):
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3

    def encode(self):
        frame = bytearray()
        frame.extend(struct.pack(">d", self.t1))
        frame.extend(struct.pack(">d", self.t2))
        frame.extend(struct.pack(">d", self.t3))

        return frame

    def decode(self, data):
        self.t1 = struct.unpack(">d",  data[0:8])[0]
        self.t2 = struct.unpack(">d",  data[8:16])[0]
        self.t3 = struct.unpack(">d",  data[16:24])[0]
