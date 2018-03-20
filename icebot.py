from icesql import *
from icethread import *
from irc import *
import os
import random
import time
import re

#####
### global variabls
#####

####
## functions that get specific info out of returned text
def toText(text):   # converts bytes to string properly
    retVal = re.findall("b'(.*)'",str(text))
    if len(retVal) > 0:
        return retVal[0]
    else:
        return ""

def getUser(text):
    if 'PRIVMSG' not in text:
        return None
    else:
        return re.findall("^:(.*?)!",text)[0]

def atNick(text,nick):
    if 'PRIVMSG' not in text:
        return False
    else:
        retVal = re.findall("[^\\s]*? PRIVMSG .*? :(.*?):? ",text)
        if len(retVal) < 1:
            return False
        else:
            return retVal[0] == nick
def atBot(text):
    return atNick(text,nickname)
####

URL = "HTTP://YOUR-ICE-RADIO.COM/"
channel = "#YOURCHANNEL"
server = "chat.freenode.net"
nickname = "icebot"
passwd = "CHANGEIT"
admin = "YOUR-ADMIN"
iceServer = "HTTP://YOUR-ICE-RADIO.COM/"

irc = IRC()
irc.connect(server,channel,nickname,passwd)

songs = []
icecheck = iceThread(1,"Ice Thread",URL,irc,channel,songs)


### variables for keeping track of icecast songs
#lastSong,song,counter = "", None, 0
###
icecheck.start()

loop = True
while loop:
    text = toText(irc.get_text())
    if (text[:4] != 'PING'):
        print (text)

    ##### Chat checkers
    if "test whisper" in text:
        irc.send(getUser(text),"psst! hey there!")
    if "testing ABC" in text:
        irc.send(channel,"received, 123!")
    if "get song" in text and atBot(text):
        print("checking the icecast server...")
        song = getSong(iceServer)
        lastSong = song
        irc.send(channel,"Current song playing is: %s" % song)
    if "last songs" in text and atBot(text):
        song = getSong(URL)
        if len(songs) < 1 or not song == songs[-1]:
            if len(songs) > 4:
                songs.remove(songs[0])
            songs.append(song)
        letters = 'abcde'[:len(songs)]
        for i in range(len(songs)):
            j = letters[i] + ") " + songs[i]
            if i==len(songs)-1:
                j = j + " [(current song)]"
            irc.send(channel,j)
    if "unmute" in text and atBot(text):
        icecheck.unmute()
        irc.send(channel,"Unmuting announcements.")
    elif "mute" in text and atBot(text):
        icecheck.mute()
        irc.send(channel,"Muting announcements.")
    ###
    ## DB interaction
    if "get faves" in text and atBot(text):
        user = getUser(text)
        faves = getFaves(user)
        if len(faves) < 1:
            irc.send(user,"You don't have any favorites saved!")
        else:
            faveString = '\n'.join([i[0] for i in faves])
            irc.send(user,"Your fave'd songs are:\n" + faveString)
    elif len(songs) > 0 and re.findall("fave ([%s])"%('abcde'[:len(songs)]),text) and atBot(text):
        user,letters = getUser(text),list('abcde')[:len(songs)]
        song = songs[letters.index(re.findall("fave ([%s])"%('abcde'[:len(songs)]),text)[0])]
        if addFave(user,song):
            irc.send(user,"%s has been added to your fave list" % song)
        else:
            irc.send(channel, "%s: %s is already a favorite!" % (user,song))
    elif "fave" in text and atBot(text):
        user,song = getUser(text),getSong(URL)
        if addFave(user,song):
            irc.send(user,"%s has been added to your fave list" % song)
        else:
            irc.send(channel,"%s: %s is already a favorite!" % (user,song))
    ## song-rating function
    #def
    ####
    #####
    if "shut it down" in text and admin == getUser(text):
        loop = False
        icecheck.finish()
    #####
    if "help" in text and atBot(text):
        irc.send(channel,"These are the commands you can use with me:\n%s\n%s\n%s\n%s\n%s\n%s\n" %
            ("\"" + nickname + ": get song\" -- I'll tell you the currently playing song.",
             "\"" + nickname + ": last songs\" -- I'll list the last 5 songs played (including the current one).",
             "\"" + nickname + ": fave\" -- Add the currently playing song to your favorites. I'll message you privately to confirm this happened.",
             "\"" + nickname + ": fave [abcde]\" -- Add song [abcde] to your favorites. Get the right letter from the \"last songs\" command.",
             "\"" + nickname + ": get faves\" -- I'll privately message you all songs in your favorites.",
             "\"shut it down\" -- ADMIN ONLY -- Shuts down the bot."))
    #####
    time.sleep(1)

icecheck.join()
