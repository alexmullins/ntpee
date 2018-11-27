import socketserver
from datetime import datetime
from common import *
# Server code


class NTPeeServer(socketserver.ThreadingUDPServer):
    """
    NTP Server
    """

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.allow_reuse_address = True
        return


class NTPeeServerHandler(socketserver.BaseRequestHandler):
    """
    NTP Server request handler
    """

    def handle(self):
        # unmarshal clientrequest
        # get timestamp t2
        # get timestamp t3
        # create ServerResponse(t1,t2,t3)
        t2 = datetime.now().timestamp()
        (data, socket) = self.request
        cr = ClientRequest()
        cr.decode(data)
        print("[+]Recv: {} sent {}".format(self.client_address[0], data.hex()))
        t3 = datetime.now().timestamp()
        sr = ServerResponse(cr.t1, t2, t3)
        packet = sr.encode()
        socket.sendto(packet, self.client_address)
        print("[+]Sent: {} was sent {}".format(
            self.client_address[0], packet.hex()))
        print("T3: {}".format(sr.t3))
        return


def main():
    #hostport = ('0.0.0.0', 9999)
    hostport = ('localhost', 9999)

    with NTPeeServer(hostport, NTPeeServerHandler) as server:
        print("Server listening on {}".format(hostport))
        server.serve_forever()


if __name__ == "__main__":
    main()
