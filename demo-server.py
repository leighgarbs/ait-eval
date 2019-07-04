from socket import *
import struct

class DemoServer:

    # Defaults
    defaultPort    = 2345
    defaultRateHz  = 1
    defaultTlmAddr = 'localhost'

    # For incoming data
    cmdPort   = defaultPort
    cmdSocket = socket(AF_INET, SOCK_DGRAM)

    # For outgoing data
    tlmPort   = defaultPort
    tlmSocket = socket(AF_INET, SOCK_DGRAM)

    # Telemetry (tlmData) is sent to this address every frame
    tlmAddr = defaultTlmAddr

    # This is the telemetry data.  It's supposed to be an unsigned 32-bit
    # integer but there doesn't seem to be any way of enforcing this with python
    tlmData = 9876

    # Server operates at this rate (Hz)
    rateHz = defaultRateHz

    def __init__(self,
                 tlmAddr = defaultTlmAddr,
                 tlmPort = defaultPort,
                 cmdPort = defaultPort,
                 rateHz  = defaultRateHz):


        # Save off the basic stuff
        self.tlmAddr = tlmAddr
        self.tlmPort = tlmPort
        self.cmdPort = cmdPort
        self.rateHz  = rateHz

        # We know enough to initialize the sockets now

        # The server must always be able to make progress, so we can't block on
        # either socket
        self.cmdSocket.setblocking(0)
        self.tlmSocket.setblocking(0)

        # This starts the cmdSocket listening
        self.cmdSocket.bind(('', self.cmdPort))

    def sendTlm(self):

        self.cmdSocket.sendto(struct.pack('I', self.tlmData),
                              (self.tlmAddr, self.tlmPort))
