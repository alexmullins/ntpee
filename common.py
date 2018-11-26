# Common code
import pathlib
import enum
import abc
import struct

DEBUG = True


def debug_print(msg):
    if DEBUG:
        print(msg)


class ConnectionClosedException(Exception):
    pass


class UnknownMsgTypeException(Exception):
    def __init__(self, code):
        self.code = code


class Message(metaclass=abc.ABCMeta):
    """
    Abstract base class for all MessageTypes.
    Each message should know how to encode itself
    to a byte array, and decode a byte array and
    update itself.
    """
    @abc.abstractmethod
    def id(self):
        """
        Should return the MsgType id for the 
        subclassed Message.
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


class MsgType(enum.IntEnum):
    ClientRequest = 1
    ServerResponse = 2


class ClientRequest(Message):
    """
    ClientRequest is sent between a NTP client and server
    recording t1. Server will send a ServerResponse containing
    t2 and t3. All timestamps are 64 bit unix timestamps (doubles)
    """

    def __init__(self, t1=None):
        self.t1 = t1

    def id(self):
        return MsgType.ClientRequest

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

    def id(self):
        return MsgType.ServerResponse

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


# dictionary mapping MsgType -> Message sublcasses
messages = dict()
messages[MsgType.ClientRequest] = ClientRequest
messages[MsgType.ServerResponse] = ServerResponse


def recvmsg(socket):
    """
    recvmsg will read an effteepee protocol message
    from the socket. it will return a tuple 
    (msgid, msg) where msgid is the id for the MsgType
    and msg is a structure matching the MsgType. 
    """
    # recv the id
    # recv the 2-byte msg len.
    # read msg len bytes from the socket.
    # pass data to parse method to return structure.
    msgid = recvid(socket)
    if not msgid in messages:
        raise UnknownMsgTypeException(msgid)
    msglen = int.from_bytes(recvall(socket, 2), byteorder="big")
    data = recvall(socket, msglen)
    msgtype = messages[msgid]
    msg = msgtype()
    msg.decode(data)
    return (msgid, msg)


def wrap_in_id_length(msgid, data):
    msglen = len(data)
    frame = bytearray()
    frame.extend(int(msgid).to_bytes(1, byteorder="big"))
    frame.extend((msglen).to_bytes(2, byteorder="big"))
    frame.extend(data)
    return bytes(frame)


def sendmsg(socket, msg):
    """
    sendmsg will send an effteepee protocol message
    on the socket. Can raise UnknownMsgTypeException.
    """
    if not msg.id() in messages:
        raise UnknownMsgTypeException(msg.id())
    data = msg.encode()
    data = wrap_in_id_length(msg.id(), data)
    socket.sendall(data)


def recvid(socket):
    """
    recvid will receive a message's id 
    and return a MsgType.
    """
    rid = recvall(socket, 1)
    msgid = MsgType(int.from_bytes(rid, byteorder="big"))
    return msgid


def recvall(socket, n):
    """
    recvall will receive all n bytes of information
    and return it as a bytes sequence. Raises a 
    ConnectionClosedException if the socket closes.
    """
    frame = bytearray()
    while len(frame) < n:
        packet = socket.recv(n - len(frame))
        if not packet:
            raise ConnectionClosedException()
        frame.extend(packet)
    return bytes(frame)
