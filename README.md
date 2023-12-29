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
  image: my_pc.png
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
- `image` (default: None), a custom image placed in the "custom" folder at the
  same level than the app root

You must define the output directory where replays exported from OBS end. This
does not configure OBS. This only tells PHOTONGENIC where to search for files so
they can be served from the Web UI.

Example:

```toml
output_local = "/mnt/r/Tinarcade/Replays"
```

You can put replays in subdirectories, in this case, the latest parent
directory name will be treated as the "group" for this replay.
