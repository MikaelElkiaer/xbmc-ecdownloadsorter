import sqlite3

class ecdb:
    def __init__(self, dbpath):
        self.__conn = sqlite3.connect(dbpath, check_same_thread=False)

    def createTable(self):
        c = self.__conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS ignored (name TEXT PRIMARY KEY);")
        self.__conn.commit()
        c.close()

    def getIgnored(self):
        c = self.__conn.cursor()
        c.execute("SELECT name FROM ignored;")
        result = c.fetchall()
        c.close()
        return result

    def addIgnored(self, name):
        c = self.__conn.cursor()
        c.execute("INSERT INTO ignored(name) VALUES(?);", [name])
        self.__conn.commit()
        c.close()

    def clearIgnored(self):
        c = self.__conn.cursor()
        c.execute("DELETE FROM ignored;")
        self.__conn.commit()
        c.close()

    def cleanIgnored(self, downloads):
        c = self.__conn.cursor()
        c.execute("CREATE TABLE temp (name TEXT PRIMARY KEY);")
        for d in downloads:
            c.execute("INSERT INTO temp(name) VALUES(?);", [d])
        c.execute("DELETE FROM ignored WHERE name NOT IN(SELECT name FROM temp);")
        c.execute("DROP TABLE temp;")
        self.__conn.commit()
        c.close()

    def close(self):
        self.__conn.close()