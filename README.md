# photongenic

Project PHOTONGENIC is a service to manage multiple OBS instances through the WebSockets API, with a focus on exporting their Replay Buffer, inspired by aixxe's REPLAY (https://aixxe.net/2023/07/revisiting-replay)

## Configuration

You must define a list of clients to connect to, in a `clients.yml` file in the
current directory, for example:

```yaml
- host: 192.168.0.14
  password: xxxx
  name: "PC 1"
- host: 192.168.0.15
  password: xxxx
  name: "PC 2"
```

Valid attributes are:

- `host`, a valid address to connect to
- `password` (default: None)
- `port` (default 4455)
- `timeout` (default 5)
- `replay` (default true), setting this to false will disable auto-starting the
  Replay Buffer on the client
- `name` (default "Client"), the only purpose is to help with debugging
- `collection` (default "Photon"), if a Scenes Collection with this name exists
  in the client, the client will switch to it right after connecting
- `scene` (default "Photon"), if a Scene witht his name exists in the client,
  the client will switch to it right after connecting

You must define a valid URL where URL + filename of the last replay serves the
file to clients in a `config.toml` file.

Example:

```toml
output_web = "https://replay-service.com/replays"
```

After exporting a replay, the user will be presented with a link in the form of
"output_web" + "/" + "filename of the last replay".
