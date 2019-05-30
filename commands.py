
# This file contains commands which are invoked  by user in Chat

from ircFunctions import *

_CHAN = ""
_q = None       # A single underscore means it's private, and won't be imported
                # using the "from x import *" syntax
_data = None

def setChannel( c ):
    global _CHAN
    _CHAN = c

def setMessageQueue( qu ):
    global _q
    _q = qu

def setData( d ):
    global _data
    _data = d

# Commands:

# Prints "This is a test"
def command_test( sender, paramArray ):
    send_message( _q, _CHAN, 'This is a test.')

# Repeats whatever is sent to it
def command_echo_parameters( sender, paramArray ):
    try:
        # Always keeps something like "ECHO: " or " " in front of the echoed
        # message, otherwise this can be exploited by users to make the bot
        # execute twitch moderation commands
        send_message( _q, _CHAN, "ECHO: " + " ".join( paramArray[1:] ) )
    except IndexError:
        send_message( _q, _CHAN, "User input could not be echoed." )

# Sends a salute
def command_greet( sender, paramArray ):
    send_message( _q, _CHAN, "o7 " + sender )

# Retrieves the points of a particular user
def command_points( sender, paramArray ):
    send_message( _q, _CHAN, sender + ", you have " + str(_data.points( sender )) + " points" )

# Distributes points out to all current viewers
def command_distribute_points( sender, paramArray ):

    amount = 1          # Default amount of points
    try:
        amount = int( paramArray[0] )
    except:
        pass

    for viewer in _data.currentViewers:
        _data.viewers[viewer][0] += amount

    _data.saveViewerData()

def command_add_authorized_user( sender, paramArray ):

    if _data.isAuthorized( paramArray[0], sender ):
        pass
    else:
        send_message( _q, _CHAN, sender + ", you are not authorized to use this command." )
        return False

    try:
        command = paramArray[1]
        user = paramArray[2].lower()
        print(user)
        added = _data.addAuthorizedUser( command, user )
        if added:
            send_message( _q, _CHAN, user + " is now authorized to use the " + command + " command." )
        else:
            send_message( _q, _CHAN, user + " could not be added to the authorized user list." )
    except IndexError:
        send_message( _q, _CHAN, "Invalid parameters. Command must be invoked as \"!command command username\"" )
