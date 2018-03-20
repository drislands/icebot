from irc import *
import threading
import time
import requests
from lxml import html

#####
### global variables
qDelay = 15
aDelay = 3600
aDelay = int(aDelay * (6/7))
SPEAK = True
MIN_LISTENERS = 2   # for the min listeners needed in order to announce
#####

class iceThread (threading.Thread):
    def __init__(self,threadID,name,URL,irc,channel,songs):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.looper = True
        self.URL = URL
        self.irc = irc
        self.channel = channel
        self.songs = songs
    def run(self):
        print ("Starting " + self.name)
        iceQuery(self)
        print ("Exiting " + self.name)
    def finish(self):
        self.looper = False
    def mute(self):
        global SPEAK
        SPEAK = False
    def unmute(self):
        global SPEAK
        SPEAK = True

###
def getHtml(URL):
    page = requests.get(URL)
    return html.fromstring(page.content)
def getSong(URL):
    tree = getHtml(URL)
    song = tree.xpath('//td[@class="streamstats"]/text()')
    return song[-1]
###
def iceQuery(thread):
    qCount = 1 # count for the song-query
    aCount = 1 # count for the announcement
    while thread.looper:
        time.sleep(1)
        listeners = int(getHtml(thread.URL).xpath('//td[@class="streamstats"]/text()')[2])
        message = ""
        if qCount % qDelay == 0:
            song = getSong(thread.URL)
            if len(thread.songs) < 1 or not song == thread.songs[-1]:
                if len(thread.songs) > 4:
                    thread.songs.remove(thread.songs[0])
                thread.songs.append(song)
                if listeners > MIN_LISTENERS+1 or aCount % aDelay == 0:
                    message = message + "Currently playing song: %s\n" % song
            qCount = 1
        else:
            qCount += 1
        if aCount % aDelay == 0:
            aCount = 1
            message = "Tune in to NAME OF RADIO STATION! There %s currently %s listener%s connected.\n%s/modradio\n" % ("is" if listeners == 1 else "are",listeners,"" if listeners == 1 else "s",thread.URL) + message
        else:
            aCount += 1
        if message != "" and SPEAK:
            print("Announcing to channel...")
            thread.irc.send(thread.channel,message)
###

#def print_time(threadName, delay, counter):
#    while counter:
#        if exitFlag:
#            threadName.exit()
#        time.sleep(delay)
#        print ("%s: %s" % (threadName, time.ctime(time.time())))
#        counter -= 1
