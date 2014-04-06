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
downloadDir = "download"
types = {"movie": 0, "tv show": 1, "sports": 2, "ignore": 3}

ftp = ecftp(path, ADDON.getSetting("username"), ADDON.getSetting("password"), downloadDir)
ftp.login()

downloads = ftp.listContent()

dbpath = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')), "settings.db")
db = ecdb(dbpath)
db.createTable()
db.cleanIgnored(downloads) #Not implemented

if "index" in PARAMS:
    ret = DIALOG.select("Choose type", sorted(types, key = types.get))
    index = int(PARAMS["index"][0])
    file = downloads[index]
    
    if ret == types["movie"]:
        ftp.move(file, ["media", "movies"])
        xbmc.executebuiltin("UpdateLibrary(video,nfs://%s/volume2/%s/%s/)" % (path, "media/movies", file) )
    if ret == types["tv show"]:
        pass #Not implemented
    if ret == types["sports"]:
        ftp.move(file, ["media", "sport"])
    if ret == types["ignore"]:
        db.addIgnored(file)

else:
    downloads = ftp.listContent()
    ignored = db.getIgnored()

    for i in range(0,len(downloads)):
        isIgnored = False

        for k in ignored:
            if k[0] == downloads[i]:
                isIgnored = True
    
        if not isIgnored:
            listitem = xbmcgui.ListItem(downloads[i], iconImage=ICON, thumbnailImage=ICON)
            xbmcplugin.addDirectoryItem(HANDLE, PATH + "?index=%d" % i, listitem, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE)

ftp.logout()

db.close()
