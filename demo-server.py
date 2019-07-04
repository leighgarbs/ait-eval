from socket import *
import struct

class DemoServer:
    ''' Simulates downlink telemetry by periodically sending an unsigned \
32-bit integer to a specified address and port.  The integer can be changed by \
sending this server the SET_UINT command from AIT.'''

    # Defaults
    defaultTlmAddr = 'localhost'
    defaultTlmPort = 2345
    defaultCmdPort = 2346
    defaultRateHz  = 1

    # For incoming data
    cmdPort   = defaultCmdPort
    cmdSocket = socket(AF_INET, SOCK_DGRAM)

    # For outgoing data
    tlmPort   = defaultTlmPort
    tlmSocket = socket(AF_INET, SOCK_DGRAM)

    # Telemetry (tlmData) is sent to this address every frame
    tlmAddr = defaultTlmAddr

    # This is the telemetry data.  It's supposed to be an unsigned 32-bit
    # integer but there doesn't seem to be any way of enforcing this with python
    tlmData = 9876

    # Commands are buffered here as they are read off the socket
    cmdBuffer = ''

    # Server operates at this rate (Hz)
    rateHz = defaultRateHz

    def __init__(self,
                 tlmAddr = defaultTlmAddr,
                 tlmPort = defaultTlmPort,
                 cmdPort = defaultCmdPort,
                 rateHz  = defaultRateHz):
        ''' Readies the telemetry and command sockets for operation. '''

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

        # This starts the cmdSocket listening on all available interfaces
        self.cmdSocket.bind(('', self.cmdPort))

    def readCmds(self):
        ''' Reads in all available commands and buffers them internally. '''
        mightBeData = True
        while(mightBeData):

            # Try to read some data
            try:
                cmdData = self.cmdSocket.recv(4096)
            except:
                print 'No data?'
                mightBeData = False
            else:
                # Add the new data to the buffer
                self.cmdBuffer += cmdData
                print 'Read ' + str(len(cmdData)) + ' bytes'

    def executeCmds(self):
        ''' Executes all buffered commands in order of reception. '''
        pass

    def sendTlm(self):
        ''' Sends a single telemetry message containing the latest received \
command data. '''
        # Assume the whole telemetry message goes out here
        self.cmdSocket.sendto(struct.pack('I', self.tlmData),
                              (self.tlmAddr, self.tlmPort))

    def frame(self):
        ''' Implements a single frame of server operation.  Reads in all \
commands, executes those commands, and then sends a single frame of \
telemetry. '''

    def run(self):
        ''' Implements the main server loop.  Does not return.  Executes one \
frame of operation at the specified rate. '''
        pass
