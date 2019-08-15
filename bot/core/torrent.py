import transmissionrpc

import logger
from bot.core.config import Config

config = Config.getConfig()

DOWNLOAD_PATH = config["DOWNLOAD_PATH"]
TRANSMISSION_HOST = config["TRANSMISSION_HOST"]
TRANSMISSION_PORT = config["TRANSMISSION_PORT"]
TRANSMISSION_USER = config["TRANSMISSION_USER"]
TRANSMISSION_PASS = config["TRANSMISSION_PASS"]

#https://pythonhosted.org/transmissionrpc/reference/transmissionrpc.html

class Torrent():

    def __init__(self):
        self.tc = transmissionrpc.Client(address=TRANSMISSION_HOST, port=TRANSMISSION_PORT,user=TRANSMISSION_USER,password=TRANSMISSION_PASS)

    def add(self,torrentUrl):
        torrent = self.tc.add_torrent(torrent=torrentUrl,download_dir=DOWNLOAD_PATH)
        logger.debug("Torrent id: %s"%str(torrent.id))
        return torrent

    def move(self,torrentId,path):
        self.tc.move_torrent_data(ids=torrentId,location=path)

    def delete(self,id,delete=True):
        status = self.tc.remove_torrent(id, delete_data=delete)
        return status

    def status(self,id):
        status = self.tc.get_torrent(id)
        logger.debug("status %s"%str(status.id))
        return status

    def allStatus(self):
        return self.tc.get_torrents()

    def pause(self,id):
        return self.tc.stop_torrent(id)

    def resume(self,id):
        return self.tc.start_torrent(id)
