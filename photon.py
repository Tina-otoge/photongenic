import socket
import typing as t
from dataclasses import dataclass
from pathlib import Path

import obsws_python as obs
import tomli
import yaml
from obsws_python.error import OBSSDKTimeoutError
from websocket import WebSocketAddressException, WebSocketTimeoutException

import audit

TIMEOUT_ERRORS = (
    OBSSDKTimeoutError,
    OSError,
    socket.timeout,
    TimeoutError,
    WebSocketAddressException,
    WebSocketTimeoutException,
)


@dataclass
class Client:
    host: str
    password: str = None
    port: int = 4455
    timeout: int = 5
    replay: bool = True
    name: str = None
    group: str = None
    collection: str = "Photon"
    scene: str = "Photon"
    image: str = None

    count = 0

    def __post_init__(self):
        self.__class__.count += 1
        self.id = self.count
        self.client = None
        self.name = self.name or self.host
        self.group = self.group or self.name
        self.start()

    def __str__(self):
        if self.name != self.group:
            return f"{self.name} ({self.group})"
        return self.name

    def start(self):
        try:
            self.client = obs.ReqClient(
                host=self.host,
                port=self.port,
                password=self.password,
                timeout=self.timeout,
            )
        except TIMEOUT_ERRORS:
            return
        try:
            self.client.get_replay_buffer_status()
        except Exception as e:
            audit.log(f"Could not get replay buffer status: {e}")
            return
        if (
            self.replay
            and not self.client.get_replay_buffer_status().output_active
        ):
            self.client.start_replay_buffer()
        if (
            self.collection
            and self.collection
            in self.client.get_scene_collection_list().scene_collections
        ):
            self.client.set_current_scene_collection(self.collection)
        if self.scene and self.scene in [
            x["sceneName"] for x in self.client.get_scene_list().scenes
        ]:
            self.client.set_current_program_scene(self.scene)
        audit.log("Connected to", self.name)

    @property
    def status(self) -> bool:
        if not self.client:
            return False
        try:
            active = self.client.get_replay_buffer_status().output_active
        except TIMEOUT_ERRORS as e:
            audit.log(
                f'Could not get replay buffer status for {self}: "{e}".'
                "\nMarking client as offline."
            )
            self.client = None
            return False
        return bool(active)


class Config:
    def __init__(self, path):
        with path.open("rb") as f:
            self._config = tomli.load(f)
        for k, v in self._config.items():
            setattr(self, k, v)

    def get(self, *args, **kwargs):
        return self._config.get(*args, **kwargs)


CLIENTS_FILE = Path("clients.yml")
CONFIG_FILE = Path("config.toml")


config = Config(CONFIG_FILE)


# load clients from yaml using safe_load
with CLIENTS_FILE.open() as f:
    clients = {
        c.id: c for c in (Client(**client) for client in yaml.safe_load(f))
    }


def get_client(id) -> t.Optional[Client]:
    if id not in clients:
        return None
    client = clients[id]
    if not client.status:
        client.start()
    return client


if __name__ == "__main__":
    for client in clients.values():
        print(client.status)
