# photongenic

Project PHOTONGENIC is a service to manage multiple OBS instances through the
WebSockets API, with a focus on exporting their Replay Buffer, inspired by
aixxe's REPLAY (https://aixxe.net/2023/07/revisiting-replay)

This is a weekend / rushed project, so quality leaves much to be desired,
functionality is prioritized over code quality, which is rare for my projects.
A rewrite might happen at some point, stay tuned!

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
- `name` (defaults to host), this helps identifying which client is what
- `group` (default to name), subtitle for the client
- `collection` (default "Photon"), if a Scenes Collection with this name exists
  in the client's OBS, the client will switch to it right after connecting
- `scene` (default "Photon"), if a Scene witht his name exists in the client's,
  OBS, the client will switch to it right after connecting
- `image` (default: None), a custom image placed in the "custom" folder at the
  same level than the app root to customize the Web UI

### `config.toml` file

You must define the output directory where replays exported from OBS end. This
does not configure OBS. This only tells PHOTONGENIC where to search for files so
they can be served from the Web UI.

Example:

```toml
output_local = "/mnt/r/Tinarcade/Replays"
```

You can put replays in subdirectories, in this case, the latest parent
directory name will be treated as the "group" for this replay.

`base_uri` (optional): Used to generate path to static files

`audit_webhook` (optional): Webhook URL to send audit logs to

`disable_wake_ui` (obsolete): Removes "wake" buttons from web UI, clients are
always auto-started now so this is redundant with other methods.

## Running

There are 3 main components in PHOTONGENIC.

- A Python module called `photon`, which is effectively the "OBS controller"
  and allows for controlling clients
- A Python module called `archive` which is used to read from the output folder
  where the replays end, and can also be run on its own to instantiate a worker
  that will generare thumbnails for videos
- A WSGI app in Flask that exposes a Web UI to control the clients from a web
  interface

Running the Web UI can be done this way:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Flask debug mode for local development
FLASK_APP=webui.app flask run --debug
# gunicorn for production
pip install gunicorn
gunicorn -w 4 webui.app:app
```

Then, you can have another process running thumbnails generation, started using
`python archive.py`.
