#!/usr/bin/env python3

# simpleircbot.py - A simple IRC-bot written in python
#
# Copyright (C) 2015 : Niklas Hempel - http://liq-urt.de
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# This is a modified version of Hempel's simple IRC-bot with a few more features
# and capabilities. Still a work in progress.

import re
import socket
import threading
import queue
import select
import time

from ircFunctions import  *
from commands import *
from alerts import *
from data import StreamerData

# --------------------------------------------- Start Settings ----------------------------------------------------
HOST = "irc.chat.twitch.tv"                     # Hostname of the IRC-Server in this case twitch's
PORT = 6667                                     # Default IRC-Port
CHAN = "#username"                              # Channelname = #{Nickname} (all lowercase)
NICK = "Username"                               # Nickname = Twitch username
PASS = "oauth:12345abc"                         # www.twitchapps.com/tmi/ will help to retrieve the required authkey

DBUG = True                                     # Enables verbose logging
VIEWERS = []
ENDNAMES = False

ENABLE_COMMANDS = True
COMMANDS = {'!test': command_test,
           '!echo': command_echo_parameters,
           'o7' : command_greet,
           '!points' : command_points,
           '!addUser' : command_add_authorized_user
           }
                                                # Dictionary of avialable commands

ENABLE_ALERTS = True
ALERTS = [ Alert( "DistributePoints", True, 60, None, command_distribute_points )

         ]                                     # List of alerts
# --------------------------------------------- End Settings -------------------------------------------------------


# --------------------------------------------- Start Functions ----------------------------------------------------
# IRC functions moved to "ircFunctions.py"
# --------------------------------------------- End Functions ------------------------------------------------------


# --------------------------------------------- Start Helper Functions ---------------------------------------------
def get_sender(msg):
    result = ""
    for char in msg:
        if char == "!":
            break
        if char != ":":
            result += char
    return result


def get_message(msg):
    result = ""
    i = 3
    length = len(msg)
    while i < length:
        result += msg[i] + " "
        i += 1
    result = result.lstrip(':')
    return result


def parse_message( sender, msg):
    if len(msg) >= 1:
        msg = msg.strip().split(' ')
        if msg[0] in COMMANDS:
            COMMANDS[msg[0]]( sender, msg )

def import_commands():
    pass

def import_alerts():
    pass
# --------------------------------------------- End Helper Functions -----------------------------------------------


# --------------------------------------------- Start Command Functions --------------------------------------------
# Commands have been moved to "commands.py"
# --------------------------------------------- End Command Functions ----------------------------------------------


# --------------------------------------------- Start Thread Functions ---------------------------------------------
def sendFromQueue():

    while True:

        # Check if the thread should exit
        if not endQueue.empty():
            if DBUG:
                print( "Closing send thread..." )
            return

        # Check for any items in the queue which need to be sent
        if not messageQueue.empty():
            msg = messageQueue.get()
            con.send( msg )
            if DBUG:
                print( "< " + msg.decode().strip() )

def readInput():

    while True:

        # Check if the thread should exit
        if not endQueue.empty():
            if DBUG:
                print( "Closing read thread..." )
            return

        # Grab user input and add it to the queue of items to send
        m = input( "" )
        if m == "QUIT":
            endQueue.put( m )
        else:
            send_message( messageQueue, CHAN, m )

def responses():

    global VIEWERS
    global ENDNAMES
    data = ""

    while True:

        # Check if the thread should exit
        if not endQueue.empty():
            if DBUG:
                print( "Closing response thread..." )
            return

        try:
            # Recieve data from the server without blocking
            ready = select.select( [con], [], [], 0 )
            if ready[0]:
                data += con.recv(1024).decode('UTF-8')
                if DBUG:
                    print( "> " + data.strip() )
                # Process the data
                data_split = re.split(r"[~\r\n]+", data)
                data = data_split.pop()

                for line in data_split:
                    line = str.rstrip(line)
                    line = str.split(line)

                    # Check what kind of message was sent by the server
                    if len(line) >= 1:

                        # PING indicates the server is just checking
                        # if we are still here
                        if line[0] == 'PING':
                            send_pong( messageQueue, line[1])

                        # Twitch seems to send info (not commands) formatted as
                        # "sender message_number recipient info"
                        if line[0] == ":{}.tmi.twitch.tv".format( CHAN[1:] ):

                            serverMessageNumber = int( line[1] )
                            recipient = line[2]

                            if serverMessageNumber == 353 and not ENDNAMES:

                                vs = line[5:]
                                for i in range( 0, len(vs)):
                                    vs[i] = vs[i][1:]
                                VIEWERS += vs

                            if serverMessageNumber == 366:

                                if DBUG:
                                    print( "Viewer List: " )
                                    print( VIEWERS )
                                streamData.initialize( VIEWERS )
                                ENDNAMES = True

                        # PRIVMSG indicates someone sent a message in chat
                        if line[1] == 'PRIVMSG':
                            sender = get_sender(line[0])
                            message = get_message(line)
                            parse_message( sender, message)

                            print(sender + ": " + message)

        except socket.error:
            print("Socket died")
            break

        except socket.timeout:
            print("Socket timeout")
            break


def timedAlerts():

    #alertList = [ Alert( "test", True, 10, "This message will repeat every 10 seconds." ) ]
    alertList = []

    prevTime = time.time()

    while True:

        # Check if the thread should exit
        if not endQueue.empty():
            if DBUG:
                print( "Closing alert thread..." )
            return

        for alert in ALERTS:
            if alert.active:
                dt = time.time() - prevTime
                alert.timer += dt
                if ( alert.timer >= alert.length ):
                    if alert.text != None:
                        send_message( messageQueue, CHAN, alert.text )
                    if alert.run != None:
                        alert.run( NICK, ["!" + alert.run.__name__] )
                    alert.reset()

        prevTime = time.time()

# --------------------------------------------- End Thread Functions -----------------------------------------------

# Create the socket and connect to the chat server
con = socket.socket()
con.connect((HOST, PORT))

# Create the endQueue to signal each thread to close,
# and the messageQueue to send messages out the socket
# in a thread-safe manner
endQueue = queue.Queue()
messageQueue = queue.Queue()
setMessageQueue( messageQueue )

setChannel( CHAN )

streamData = StreamerData()
setData( streamData )
#streamData.initialize()

# Create the thread which sends messages from the message queue
senderThread = threading.Thread( target=sendFromQueue )
senderThread.start()

# Connect to the chat room using IRC protocol
send_pass( messageQueue, PASS)
send_nick( messageQueue, NICK)
join_channel( messageQueue, CHAN)

# Create the thread which reads user input and sends it to chat
readThread = threading.Thread( target=readInput )
readThread.start()

if ( ENABLE_COMMANDS ):
    # Create the thread which monitors chat for commands and executes them
    responseThread = threading.Thread( target=responses )
    responseThread.start()

if ( ENABLE_ALERTS ):
    # Create the thread which sends timed alerts into chat
    alertThread = threading.Thread( target=timedAlerts )
    alertThread.start()

# Join each thread back into the main thread, blocking until they are done
senderThread.join()
readThread.join()
if ( ENABLE_COMMANDS ):
    responseThread.join()
if (ENABLE_ALERTS):
    alertThread.join()

streamData.save()

# Close the socket before exiting
con.close()
