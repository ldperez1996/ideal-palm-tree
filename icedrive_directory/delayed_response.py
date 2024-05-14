"""Servant implementation for the delayed response mechanism."""

import Ice

import IceDrive


class DirectoryQueryResponse(IceDrive.DirectoryServiceQueryResponse):
    """Query response receiver."""
    def __init__(self, communicator: Ice.Communicator):
        self.topic_manager = IceDrive.TopicManagerPrx.checkedCast(
            communicator.propertyToProxy("IceStorm.TopicManager.Proxy")
        )
        self.topic = self.topic_manager.retrieve("DirectoryQueryTopic")
        self.topic.subscribeAndGetPublisher({}, self)
        self.directory_service = None  # Referencia al servicio de directorio

    def setDirectoryService(self, directory_service: IceDrive.DirectoryServicePrx):
        self.directory_service = directory_service

    def rootDirectoryResponse(self, root: IceDrive.DirectoryPrx, current: Ice.Current = None) -> None:
        """Receive a Directory when other service instance knows the user."""
        print("Received root directory response:", root)
        if self.directory_service:
            try:
                self.directory_service.getRoot().rootDirectoryResponse(root)
            except Ice.Exception as e:
                print("Error sending root directory response:", e)

class DirectoryQuery(IceDrive.DirectoryServiceQuery):
    """Query receiver."""
    def __init__(self, communicator: Ice.Communicator):
        self.topic_manager = IceDrive.TopicManagerPrx.checkedCast(
            communicator.propertyToProxy("IceStorm.TopicManager.Proxy")
        )
        self.topic = self.topic_manager.retrieve("DirectoryQueryTopic")
        self.directory_query_response = DirectoryQueryResponse(communicator)

    def rootDirectory(self, user: IceDrive.UserPrx, response: IceDrive.DirectoryServiceQueryResponsePrx, current: Ice.Current = None) -> None:
        """Receive a query about the user's root directory."""
        print("Sending root directory query for user:", user)
        self.directory_query_response.setDirectoryService(response)
        self.topic.publish("rootDirectory", user, self.directory_query_response)