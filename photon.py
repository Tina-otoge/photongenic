import dataclasses
from dataclasses import dataclass
from pathlib import Path

import obsws_python as obs
import tomli
import yaml
from websocket import WebSocketAddressException


@dataclass
class Client:
    host: str
    password: str = None
    port: int = 4455
    timeout: int = 5
    replay: bool = True
    name: str = "Client"
    collection: str = "Photon"
    scene: str = "Photon"
    image: str = None

    count = 0

    def __post_init__(self):
        self.count += 1
        self.id = self.count
        self.client = None

    def start(self):
        try:
            self.client = obs.ReqClient(
                host=self.host,
                port=self.port,
                password=self.password,
                timeout=self.timeout,
            )
        except (TimeoutError, WebSocketAddressException) as e:
            print(f"Could not establish connection to {self}: {e}")
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

    @property
    def status(self) -> dict:
        if not self.client:
            active = False
        else:
            active = self.client.get_replay_buffer_status().output_active
        return dict(
            **dataclasses.asdict(self),
            active=active,
        )


class Config:
    def __init__(self, path):
        with path.open("rb") as f:
            for k, v in tomli.load(f).items():
                setattr(self, k, v)


CLIENTS_FILE = Path("clients.yml")
CONFIG_FILE = Path("config.toml")


config = Config(CONFIG_FILE)


# load clients from yaml using safe_load
with CLIENTS_FILE.open() as f:
    clients = {
        c.id: c for c in (Client(**client) for client in yaml.safe_load(f))
    }
