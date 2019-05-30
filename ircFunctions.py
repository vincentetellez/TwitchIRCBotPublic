
def send_pong( q, msg):
    #con.send(bytes('PONG %s\r\n' % msg, 'UTF-8'))
    q.put( bytes('PONG %s\r\n' % msg, 'UTF-8') )
    #print( '< PONG %s' % msg )


def send_message( q, chan, msg):
    q.put(bytes('PRIVMSG %s :%s\r\n' % (chan, msg), 'UTF-8'))
    #print( '< PRIVMSG %s :%s' % (chan, msg) )


def send_nick( q, nick):
    q.put(bytes('NICK %s\r\n' % nick, 'UTF-8'))
    #print( '< NICK %s' % nick )


def send_pass( q, password):
    q.put(bytes('PASS %s\r\n' % password, 'UTF-8'))
    #print( '< PASS %s' % password )


def join_channel( q, chan):
    q.put(bytes('JOIN %s\r\n' % chan, 'UTF-8'))
    #print( '< JOIN %s' % chan )


def part_channel( q, chan):
    q.put(bytes('PART %s\r\n' % chan, 'UTF-8'))
    #print( '< PART %s' % chan )
