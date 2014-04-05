from ftplib import FTP

class unsorted:

    def __init__(self, path, username, password, workingDir):
        self.__ftp = FTP(host=path, timeout=300)

        self.__username = username
        self.__password = password
        self.__workingDir = workingDir

    def login(self):
        msg = self.__ftp.login(user=self.__username, passwd=self.__password)
        self.__ftp.cwd(self.__workingDir)

        return msg == '230 User %s logged in.' % self.__username

    def logout(self):
        self.__ftp.quit()

    def listContent(self):
        list = self.__ftp.nlst()
        return list

    def move(self, fileName, targetPath):

        old = "/" + self.__workingDir + "/" + fileName
        new = "/"
        for path in targetPath:
            new = new + path + "/"

        new = new + fileName

        print old
        print new
        self.__ftp.rename(old, new)