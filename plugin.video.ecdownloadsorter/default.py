import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import os
import sys
import urlparse

#Addon info
ADDON = xbmcaddon.Addon()
NAME = ADDON.getAddonInfo("name")
ICON = ADDON.getAddonInfo("icon")
PATH = ADDON.getAddonInfo("path")
sys.path.append(xbmc.translatePath(os.path.join(PATH, "resources", "lib" )))
DIALOG = xbmcgui.Dialog()

#Imports after path append
from ecftp import ecftp
from ecdb import ecdb

#Addon state
PATH = sys.argv[0]
HANDLE = int(sys.argv[1])
PARAMS = urlparse.parse_qs(sys.argv[2][1:])

if ADDON.getSetting("path") == "":
    ADDON.openSettings()

path = ADDON.getSetting("path")
username = ADDON.getSetting("username")
password = ADDON.getSetting("password")
downloadDir = "download"
types = {"movie": 0, "tv show": 1, "sports": 2, "ignore": 3}

dbpath = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')), "settings.db")

if "index" in PARAMS:
    ret = DIALOG.select("Choose type", sorted(types, key = types.get))

    index = int(PARAMS["index"][0])

    ftp = ecftp(path, username, password, downloadDir)
    ftp.login()

    downloads = ftp.listContent()

    file = downloads[index]
    
    if ret == types["movie"]:
        ftp.move(file, ["media", "movies"])
        xbmc.executebuiltin("UpdateLibrary(video,nfs://%s/volume2/%s/%s/)" % (path, "media/movies", file) )
        ftp.logout()
    if ret == types["tv show"]:
        pass #Not implemented
    if ret == types["sports"]:
        ftp.move(file, ["media", "sport"])
        ftp.logout()
    if ret == types["ignore"]:
        db = ecdb(dbpath)
        db.addIgnored(file)
        db.close()

ftp = ecftp(path, username, password, downloadDir)
ftp.login()

downloads = ftp.listContent()

db = ecdb(dbpath)
db.createTable()
db.cleanIgnored(downloads)

ignored = db.getIgnored()

for i in range(0, len(downloads)):
    isIgnored = False

    for k in ignored:
        if k[0] == downloads[i]:
            isIgnored = True
    
    if not isIgnored:
        listitem = xbmcgui.ListItem(downloads[i])
        xbmcplugin.addDirectoryItem(HANDLE, PATH + "?index=%d" % i, listitem, isFolder=True, totalItems=len(downloads))

xbmcplugin.endOfDirectory(HANDLE, updateListing=True)

db.close()

ftp.logout()
