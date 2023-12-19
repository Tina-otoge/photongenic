import datetime
from pathlib import Path

import flask

import photon

Flask = flask.Flask
OK = flask.Response(status=200)

app = Flask(__name__, template_folder=".")


@app.context_processor
def inject_globals():
    return {"photon": photon}


@app.route("/")
def index():
    return flask.render_template("template.html")


@app.post("/<int:id>/export")
def export(id):
    client: photon.Client = photon.clients[id]
    client.client.save_replay_buffer()
    replay_path = (
        client.client.get_last_replay_buffer_replay().saved_replay_path
    )
    src = Path(replay_path)
    return {
        "url": f"{photon.config.output_web}/{src.name}",
    }

    # Moving the file does not make sense if the server and the client are
    # running on different machines. Will maybe need an agent on the client.
    now = datetime.datetime.now()
    dest_name = f"{client.name} {now}.{src.suffix}"
    dest = Path(photon.config.output_path) / dest_name
    dest.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dest)
    return {
        "url": photon.config.output_url + dest_name,
    }
