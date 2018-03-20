import socket
import threading
import sys
import time

COLOR = "\x0311"
delay = 1

def b(text):
    return bytes(text,"UTF-8")

class IRC:

    # i don't think we need this line, i think i just mindlessly copied this from the site i was working from
    #irc = socket.socket()

    def __init__(self):
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send(self, chan, msg):
        if '\n' in msg:
            longMsg = messageQueue(self,chan,msg)
            longMsg.start()
        else:
            self.irc.send(b("PRIVMSG " + chan + " :" + COLOR + msg + "\n"))

    def connect(self, server, channel, botnick, passwd):
        #defines the socket
        print ("connecting to:" + server)
        self.irc.connect((server,6667)) # 6667 is normal; 6697 for SASL
        self.irc.send(b("PASS " + passwd + "\n"))
        self.irc.send(b("USER " + botnick + " " + botnick + " " + botnick + " :This is a fun bot!\n"))
        self.irc.send(b("NICK " + botnick + "\n"))
        self.irc.send(b("JOIN " + channel + "\n"))

    def get_text(self):
        text = self.irc.recv(2040) # receive the text
        text = text.strip(b('\n\r'))

        if text.find(b('PING')) != -1:
            self.irc.send(b("PONG :pingis\n"))

        return (text)


class messageQueue(threading.Thread):
    def __init__(self,irc,chan,msg):
        threading.Thread.__init__(self)
        self.irc = irc
        self.chan = chan
        self.msg = msg
    def run(self):
        for i in self.msg.split('\n'):
            if i != "":
                self.irc.send(self.chan,i)
                time.sleep(delay)
