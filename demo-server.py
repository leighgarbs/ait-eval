#!/usr/bin/env python

import argparse
import datetime
import socket
import struct
import time

# Defaults
defaultTlmAddr = 'localhost'
defaultTlmPort = 2345
defaultCmdPort = 2346
defaultRateHz  = 1

class DemoServer:
    ''' Simulates downlink telemetry by periodically sending an unsigned \
32-bit integer to a specified address and port.  The integer can be changed by \
sending this server the SET_UINT command from AIT.'''

    # For incoming data
    cmdPort   = defaultCmdPort
    cmdSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # For outgoing data
    tlmPort   = defaultTlmPort
    tlmSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Telemetry (tlmData) is sent to this address every frame
    tlmAddr = defaultTlmAddr

    # This is the telemetry data.  It's supposed to be an unsigned 32-bit
    # integer but there doesn't seem to be any way of enforcing this with python
    tlmData = 9876

    # Commands are buffered here as they are read off the socket
    cmdBuffer = ''

    # Frames are this long
    frameDuration = datetime.timedelta(0, 1.0 / defaultRateHz)

    def __init__(self,
                 tlmAddr = defaultTlmAddr,
                 tlmPort = defaultTlmPort,
                 cmdPort = defaultCmdPort,
                 rateHz  = defaultRateHz):
        ''' Readies the telemetry and command sockets for operation. '''

        # Save off the basic stuff
        self.tlmAddr       = tlmAddr
        self.tlmPort       = tlmPort
        self.cmdPort       = cmdPort
        self.frameDuration = datetime.timedelta(0, 1.0 / rateHz)

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
            except socket.error:
                mightBeData = False
            else:
                # Add the new data to the buffer
                self.cmdBuffer += cmdData

    def executeCmds(self):
        ''' Executes all buffered commands in order of reception. '''

        # Can't do anything unless we have a full AIT command's worth of data
        while(len(self.cmdBuffer) >= 106):
            # Grab the data we care about, ignore the rest
            self.tlmData = struct.unpack('>3xI', self.cmdBuffer[:7])[0]
            self.cmdBuffer = self.cmdBuffer[106:]
            print self.tlmData

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

        self.readCmds()
        self.executeCmds()
        self.sendTlm()

    def run(self):
        ''' Implements the main server loop.  Does not return.  Executes one \
frame of operation at the specified rate. '''

        while(True):

            frameStart = datetime.datetime.now()

            # Execute a frame
            self.frame()

            # How long did the frame take?
            frameTime = datetime.datetime.now() - frameStart

            # Sleep off the rest of the frame
            if (frameTime < self.frameDuration):
                time.sleep((self.frameDuration - frameTime).total_seconds())

# End of the DemoServer class definition

# This will get executed when this file is run as a script
if __name__ == '__main__':

    description = \
    'Simulates downlink telemetry by periodically sending an unsigned 32-bit ' \
    'integer to a specified address and port.  The integer can be changed by ' \
    'sending this server the SET_UINT command from AIT.  Both commands and ' \
    'telemetry use UDP.'

    parser = argparse.ArgumentParser(description)

    parser.add_argument('--tlm-address',
                        default = defaultTlmAddr,
                        help = 'IPv4 address to which telemetry will be sent')
    parser.add_argument('--tlm-port',
                        type = int,
                        default = defaultTlmPort,
                        help = 'Port to which telemetry will be sent')
    parser.add_argument('--cmd-port',
                        type = int,
                        default = defaultCmdPort,
                        help = 'Port on which commands are received')
    parser.add_argument('--rate-hz',
                        type = float,
                        default = defaultRateHz,
                        help = 'Rate (Hz) of server updates')

    args = parser.parse_args()

    DemoServer().run()
