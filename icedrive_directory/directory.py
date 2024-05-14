"""Module for servants implementations."""

import Ice
import os
import IceDrive


class Directory(IceDrive.Directory):
    """Implementation of the IceDrive.Directory interface."""

    def __init__(self, path: str, user: IceDrive.UserPrx):
        self.path = path
        self.user = user
        self.children = {}  # Almacenamiento de directorios hijos
        self.files = {}  # Almacenamiento de archivos enlazados

    def getParent(self, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to the parent directory, if it exists. None in other case."""
        parent_path = os.path.dirname(self.path)
        if parent_path == self.path:
            raise IceDrive.RootHasNoParent()
        return Directory(parent_path, self.user)

    def getPath(self, current: Ice.Current = None) -> str:
        """Return the path for the directory within the user space."""
        return self.path

    def getChilds(self, current: Ice.Current = None) -> list[str]:
        """Return a list of names of the directories contained in the directory."""
        return list(self.children.keys())

    def getChild(self, name: str, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy to one specific directory inside the current one."""
        if name not in self.children:
            raise IceDrive.ChildNotExists(name, self.path)
        return self.children[name]

    def createChild(
        self, name: str, current: Ice.Current = None
    ) -> IceDrive.DirectoryPrx:
        """Create a new child directory and returns its proxy."""
        if name in self.children:
            raise IceDrive.ChildAlreadyExists(name, self.path)
        child_path = os.path.join(self.path, name)
        self.children[name] = Directory(child_path, self.user)
        return self.children[name]

    def removeChild(self, name: str, current: Ice.Current = None) -> None:
        """Remove the child directory with the given name if exists."""
        if name not in self.children:
            raise IceDrive.ChildNotExists(name, self.path)
        del self.children[name]

    def getFiles(self, current: Ice.Current = None) -> list[str]:
        """Return a list of the files linked inside the current directory."""
        return list(self.files.keys())

    def getBlobId(self, filename: str, current: Ice.Current = None) -> str:
        """Return the "blob id" for a given file name inside the directory."""
        if filename not in self.files:
            raise IceDrive.FileNotFound(filename)
        return self.files[filename]

    def linkFile(
        self, filename: str, blob_id: str, current: Ice.Current = None
    ) -> None:
        """Link a file to a given blob_id."""
        if filename in self.files:
            raise IceDrive.FileAlreadyExists(filename)
        self.files[filename] = blob_id

    def unlinkFile(self, filename: str, current: Ice.Current = None) -> None:
        """Unlink (remove) a filename from the current directory."""
        if filename not in self.files:
            raise IceDrive.FileNotFound(filename)
        del self.files[filename]

class DirectoryService(IceDrive.DirectoryService):
    """Implementation of the IceDrive.Directory interface."""
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.users = {}  # Almacenamiento de directorios raíz por usuario

    def getRoot(self, user: IceDrive.UserPrx, current: Ice.Current = None) -> IceDrive.DirectoryPrx:
        """Return the proxy for the root directory of the given user."""
        if user not in self.users:
            self.users[user] = Directory(os.path.join(self.root_path, user.getUsername()), user)
        return self.users[user]
    
    def setRootPath(self, root_path: str, current: Ice.Current = None) -> None:
        """Set the root path for the directory service."""
        self.root_path = root_path

    def getUsers(self, current: Ice.Current = None) -> list[IceDrive.UserPrx]:
        """Return a list of users with root directories in the service."""
        return list(self.users.values())