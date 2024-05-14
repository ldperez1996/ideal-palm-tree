"""Authentication service application."""

import Ice
import logging
import sys
from typing import List

from .directory import DirectoryService
from .discovery import Discovery

class DirectoryApp(Ice.Application):
    """Implementation of the Ice.Application for the Authentication service."""

    def run(self, args: List[str]) -> int:
        """Execute the code for the AuthentacionApp class."""
        adapter = self.communicator().createObjectAdapter("DirectoryAdapter")
        adapter.activate()

        servant = DirectoryService()
        servant_proxy = adapter.addWithUUID(servant)

        logging.info("Proxy: %s", servant_proxy)

        # Crear una instancia del servicio de descubrimiento
        discovery = Discovery(self.communicator())

        # Anunciar el servicio de directorio al servicio de descubrimiento
        discovery.announceDirectoryService(servant_proxy)

        # Obtener los servicios de autenticación y almacenamiento de blobs del servicio de descubrimiento
        authentication_services = discovery.getAuthenticationServices()
        blob_services = discovery.getBlobServices()

        # Realizar operaciones con los servicios descubiertos
        for auth_service in authentication_services:
            print("Discovered Authentication Service:", auth_service)
        
        for blob_service in blob_services:
            print("Discovered Blob Service:", blob_service)

        self.shutdownOnInterrupt()
        self.communicator().waitForShutdown()

        return 0


def main():
    """Handle the icedrive-authentication program."""
    app = DirectoryApp()
    return app.main(sys.argv)
