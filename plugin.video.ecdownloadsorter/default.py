import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import os
import sys
import urlparse
import sqlite3

ADDON = xbmcaddon.Addon()
NAME = ADDON.getAddonInfo("name")
ICON = ADDON.getAddonInfo("icon")
PATH = ADDON.getAddonInfo("path")
sys.path.append(xbmc.translatePath(os.path.join(PATH, "resources", "lib" )))

from unsorted import unsorted

PATH = sys.argv[0]
HANDLE = int(sys.argv[1])
PARAMS = urlparse.parse_qs(sys.argv[2][1:])

if ADDON.getSetting("path") == "":
    ADDON.openSettings()

path = ADDON.getSetting("path")
downloadDir = ADDON.getSetting("downloadDir")
unsorted = unsorted(path,
                ADDON.getSetting("username"),
                ADDON.getSetting("password"),
                downloadDir)

unsorted.login()

downloadsList = unsorted.listContent()

dbpath = os.path.join(xbmc.translatePath(ADDON.getAddonInfo('profile')), "settings.db")
conn = sqlite3.connect(dbpath, check_same_thread=False)

def sqlite_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        dot = col[0].find('.') + 1
        if dot != -1:
            d[col[0][dot:]] = row[idx]
        else:
            d[col[0]] = row[idx]
    return d

conn.row_factory = sqlite_dict_factory

c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS ignored (name TEXT PRIMARY KEY);")
conn.commit()
c.close()

c = conn.cursor()
c.execute("SELECT name FROM ignored;")
ignored = c.fetchall()
c.close()

if "index" in PARAMS:
    dialog = xbmcgui.Dialog()
    ret = dialog.select("Choose category", ["Movie", "TV Show", "Sports", "Ignore"])
    
    if ret == 0:
        unsorted.move(downloadsList[int(PARAMS["index"][0])], ["media", "movies"])
        xbmc.executebuiltin("UpdateLibrary(video,nfs://%s/volume2/%s/%s/)" % (path, "media/movies", downloadsList[int(PARAMS["index"][0])]))
    if ret == 1:
        pass
    if ret == 2:
        unsorted.move(downloadsList[int(PARAMS["index"][0])], ["media", "sport"])
    if ret == 3:
        c = conn.cursor()
        c.execute("INSERT INTO ignored(name) VALUES(?);", [downloadsList[int(PARAMS["index"][0])]])
        conn.commit()
        c.close()

else:
    downloadsList = unsorted.listContent()

    for i in range(0,len(downloadsList)):
        isIgnored = False

        for k in ignored:
            if k["name"] == downloadsList[i]:
                isIgnored = True
    
        if not isIgnored:
            listitem = xbmcgui.ListItem(downloadsList[i], iconImage=ICON, thumbnailImage=ICON)
            xbmcplugin.addDirectoryItem(HANDLE, PATH + "?index=%d" % i, listitem, isFolder=True)

    xbmcplugin.endOfDirectory(HANDLE)

unsorted.logout()

conn.close()
