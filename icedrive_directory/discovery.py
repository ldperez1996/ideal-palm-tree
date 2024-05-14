"""Servant implementations for service discovery."""

import Ice
import IceDrive
import threading
import time


class Discovery(IceDrive.Discovery):
    """Servants class for service discovery."""

    def __init__(self, communicator: Ice.Communicator):
        self.topic_manager = IceDrive.TopicManagerPrx.checkedCast(
            communicator.propertyToProxy("IceStorm.TopicManager.Proxy")
        )
        self.topic = self.topic_manager.retrieve("DiscoveryTopic")
        self.authentication_services = []
        self.directory_services = []
        self.blob_services = []
        self.announcement_interval = 10  # Intervalo de anuncio en segundos
        self.announcement_thread = threading.Thread(target=self.sendAnnouncements)
        self.announcement_thread.daemon = True
        self.announcement_thread.start()

    def sendAnnouncements(self):
        while True:
            if self.authentication_services:
                self.topic.publish("announceAuthentication", self.authentication_services[0])
            if self.directory_services:
                self.topic.publish("announceDirectoryService", self.directory_services[0])
            if self.blob_services:
                self.topic.publish("announceBlobService", self.blob_services[0])
            time.sleep(self.announcement_interval)

    def announceAuthentication(self, prx: IceDrive.AuthenticationPrx, current: Ice.Current = None) -> None:
        """Receive an Authentication service announcement."""
        self.authentication_services.append(prx)
        print("Received authentication service announcement:", prx)

    def announceDirectoryServices(self, prx: IceDrive.DirectoryServicePrx, current: Ice.Current = None) -> None:
        """Receive an Directory service announcement."""
        self.directory_services.append(prx)
        print("Received directory service announcement:", prx)

    def announceBlobService(self, prx: IceDrive.BlobServicePrx, current: Ice.Current = None) -> None:
        """Receive an Blob service announcement."""
        self.blob_services.append(prx)
        print("Received blob service announcement:", prx)

    def getAuthenticationServices(self, current: Ice.Current = None) -> list[IceDrive.AuthenticationPrx]:
        """Return a list of the discovered Authentication*"""
        return self.authentication_services

    def getDiscoveryServices(self, current: Ice.Current = None) -> list[IceDrive.DirectoryServicePrx]:
        """Return a list of the discovered DirectoryService*"""
        return self.directory_services

    def getBlobServices(self, current: Ice.Current = None) -> list[IceDrive.BlobServicePrx]:
        """Return a list of the discovered BlobService*"""
        return self.blob_services