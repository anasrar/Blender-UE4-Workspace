import os
import abc
from abc import ABC, abstractmethod

from . remote_execution import REMOTE_EXEC, RemoteExecutionConfig

class AbstractConnect(ABC):

    @property
    @abstractmethod
    def _remote(self):
        pass

    @abstractmethod
    def connect(self, DEFAULT_MULTICAST_TTL=0, DEFAULT_MULTICAST_GROUP_ENDPOINT=('239.0.0.1', 6766), DEFAULT_MULTICAST_BIND_ADDRESS='0.0.0.0', DEFAULT_COMMAND_ENDPOINT=('127.0.0.1', 6776)):
        pass

    @property
    @abstractmethod
    def is_connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def exec_script(self, script='ImportStaticMesh.py'):
        pass

class ConnectToUnrealEngine(AbstractConnect):

    _remote = REMOTE_EXEC

    def connect(self, DEFAULT_MULTICAST_TTL=0, DEFAULT_MULTICAST_GROUP_ENDPOINT=('239.0.0.1', 6766), DEFAULT_MULTICAST_BIND_ADDRESS='0.0.0.0', DEFAULT_COMMAND_ENDPOINT=('127.0.0.1', 6776)):
        self._remote.start(config=RemoteExecutionConfig(DEFAULT_MULTICAST_TTL=DEFAULT_MULTICAST_TTL, DEFAULT_MULTICAST_GROUP_ENDPOINT=DEFAULT_MULTICAST_GROUP_ENDPOINT, DEFAULT_MULTICAST_BIND_ADDRESS=DEFAULT_MULTICAST_BIND_ADDRESS, DEFAULT_COMMAND_ENDPOINT=DEFAULT_COMMAND_ENDPOINT))

    @property
    def is_connect(self):
        return not (self._remote._broadcast_connection is None)

    def disconnect(self):
        self._remote.stop()

    @property
    def remote_nodes(self):
        return self._remote.remote_nodes

    def exec_script(self, script='ImportStaticMesh.py'):
        for node_id in [user['node_id'] for user in self._remote.remote_nodes]:
            self._remote.open_command_connection(node_id)
            script_path = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'ue4_script', script)).replace(os.sep, '/')
            addon_path = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')).replace(os.sep, '/')
            self._remote.run_command('exec(open("' + script_path + '").read(), {"addon_path": "' + addon_path + '", "node_id": "' + str(node_id) + '"})', exec_mode='ExecuteStatement')
            self._remote.close_command_connection()

remote = ConnectToUnrealEngine()
skeletons = []