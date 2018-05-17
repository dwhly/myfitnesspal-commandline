#!/usr/bin/env python2.7
# keep.py is used for xmpp communication between digitalocean server and laptop/mobile xmpp chat client for myfitnesspal project
# starting code from http://off-the-stack.moorman.nu/2012-10-10-keep-in-touch-with-your-servers-using-xmpp.html
# code modified by Aleksandar Josifoski 2018 May
"""
Prototype client for simple monitoring purposes.

"""
import os
import time
import traceback
import xmpp
import codecs
import glob

# dir_in is directory where project files will be placed, assuming that on server
# username is mfp and directory is also called mfp
dir_in = '/home/mfp/mfp/'

# In CLIENT_JID you set server xmpp account
# Example: CLIENT_JID = "dwhly-server@xmpp.jp"
CLIENT_JID = ""
CLIENT_PASSWORD = ""

# In AUTHORIZED_JIDS list you set personal xmpp accounts
# Example AUTHORIZED_JIDS = ["mypersonal1@xmpp.jp", "mypersonal2@xmpp.jp"]
AUTHORIZED_JIDS = []

mysender = ''
mymessage_type = None

def writetocommandtxt(command):
    ''' this function will append command to line_commands.txt '''
    with codecs.open(dir_in + 'command.txt'.strip(), 'w', 'utf-8') as fout:
        fout.write(str(command))
        
def handle_responses(client):
    ''' function to handle responses '''
    lr = glob.glob(dir_in + 'responses/' + '*.txt')
    lr.sort()
    for resp in lr:
        fresp = codecs.open(resp, 'r', 'utf-8')
        line = fresp.read()
        line = line.strip()
        fresp.close()
        message = line
        client.send(xmpp.Message(mysender, message, typ=mymessage_type))
        os.remove(resp)

def handle_messages(jids, commands):
    """
    Returns a stanza handler function which executes given commands
    from the provided jids.
    """
    def handler(client, stanza):
        """
        Handler which executes given commands from authorized jids.
        """
        global mysender
        global mymessage_type
        sender = stanza.getFrom()
        mysender = sender
        #print(str(sender) + '*' * 100)
        message_type = stanza.getType()
        mymessage_type = message_type
        if any([sender.bareMatch(x) for x in jids]):
            command = stanza.getBody()
            #print(str(command) + '*' * 100)
            if str(command) != 'None':
                writetocommandtxt(command)

    return handler

def handle_presences(jids):
    """
    Returns a stanza handler function which automatically authorizes
    incoming presence requests from the provided jids.
    """
    def handler(client, stanza):
        """
        Handler which automatically authorizes subscription requests
        from authorized jids.
        """
        sender = stanza.getFrom()
        presence_type = stanza.getType()
        if presence_type == "subscribe":
            if any([sender.bareMatch(x) for x in jids]):
                client.send(xmpp.Presence(to=sender, typ="subscribed"))
    return handler


def run_client(client_jid, client_password, authorized_jids):
    """
    Initializes and runs a fresh xmpp client (blocking).
    """
    high_load = 5
    commands = {
        "stats": lambda *args: os.popen("uptime").read().strip(),
    }

    # Initialize and connect the client.
    jid = xmpp.JID(client_jid)
    client = xmpp.Client(jid.domain)
    if not client.connect():
        return

    # Authenticate.
    if not client.auth(jid.node, client_password, jid.resource):
        return

    # Register the message handler which is used to respond
    # to messages from the authorized contacts.
    message_callback = handle_messages(authorized_jids, commands)
    client.RegisterHandler("message", message_callback)

    # Register the presence handler which is used to automatically
    # authorize presence-subscription requests from authorized contacts.
    presence_callback = handle_presences(authorized_jids)
    client.RegisterHandler("presence", presence_callback)

    # Go "online".
    client.sendInitPresence()
    client.Process()

    # Finally, loop, update the presence according to the load and
    # "sleep" for a while.
    previous_load_maximum = 0
    while client.isConnected():
        # Determine the load averages and the maximum of the 1, 10 and 15 minute
        # averages.
        # In case the maximum is above the "high_load" value, the status will be
        # set to "do not disturb" with the load averages as status message.
        # The status will be updated continuously once we reached high load.
        # When the load decreases and the maximum is below the "high_load" value
        # again, the status is reset to "available".
        load = os.getloadavg()
        load_string = "load: %s %s %s" % load
        load_maximum = max(list(load))
        if load_maximum >= high_load:
            client.send(xmpp.Presence(show="dnd", status=load_string))
        elif load_maximum < high_load and previous_load_maximum >= high_load:
            client.send(xmpp.Presence())
        previous_load_maximum = load_maximum

        # Handle stanzas and sleep.
        client.Process()
        handle_responses(client)
        time.sleep(1)


if __name__ == "__main__":

    # Loop until the program is terminated.
    # In case of connection problems and/or exceptions, the client is
    # run again after a delay.
    while True:
        print "Trying to connect ..."
        try:
            run_client(CLIENT_JID, CLIENT_PASSWORD, AUTHORIZED_JIDS)
        except Exception, e:
            print "Caught exception!"
            traceback.print_exc()
        print "Not connected - attempting reconnect in a moment."
        time.sleep(10)
