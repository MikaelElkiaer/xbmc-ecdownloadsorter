import sys
import urlparse
import xbmcgui

PARAMS = urlparse.parse_qs(sys.argv[2][1:])
types = {"movie": 0, "tv show": 1, "sports": 2, "ignore": 3}

if "index" in PARAMS:
    isUpdateMode = True
    ret = xbmcgui.Dialog().select("Choose type", sorted(types, key = types.get))
else:
    isUpdateMode = False
    ret = -1

import xbmc
import xbmcaddon
import xbmcplugin
import os
from ecftp import ecftp
from ecdb import ecdb

#Addon state
ADDON = xbmcaddon.Addon()
PATH = sys.argv[0]
HANDLE = int(sys.argv[1])

path = ADDON.getSetting("path")
username = ADDON.getSetting("username")
password = ADDON.getSetting("password")
downloadDir = "download"

dbpath = os.path.join(xbmc.translatePath(ADDON.getAddonInfo("profile")), "settings.db")

ftp = ecftp(path, username, password, downloadDir)
ftp.login()

db = ecdb(dbpath)

downloads = ftp.listContent()

if ret != -1:
    index = int(PARAMS["index"][0])
    file = downloads.pop(index)
    
    if ret == types["movie"]:
        ftp.move(file, ["media", "movies"])
        xbmc.executebuiltin("UpdateLibrary(video,nfs://%s/volume2/%s/%s/)" % (path, "media/movies", file) )
    elif ret == types["tv show"]:
        pass #Not implemented
    elif ret == types["sports"]:
        ftp.move(file, ["media", "sport"])
    elif ret == types["ignore"]:
        db = ecdb(dbpath)
        db.addIgnored(file)

if not isUpdateMode:
    db.createTable()
    db.cleanIgnored(downloads)

ignored = db.getIgnored()
downloadsSize = len(downloads)

for i in range(0, downloadsSize):
    isIgnored = False

    for k in ignored:
        if k[0] == downloads[i]:
            isIgnored = True
    
    if not isIgnored:
        listitem = xbmcgui.ListItem(downloads[i])
        xbmcplugin.addDirectoryItem(HANDLE, PATH + "?index=%d" % i, listitem, isFolder=True, totalItems=downloadsSize)
        
db.close()
ftp.logout()

xbmcplugin.endOfDirectory(HANDLE, updateListing=isUpdateMode)
