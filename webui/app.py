from pathlib import Path

import flask
from flask import Blueprint, Flask

import archive
import audit
import photon

OK = flask.Response(status=200)

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = photon.config.get("base_uri")
custom = Blueprint("custom", __name__, static_folder="../custom")
replay_files = Blueprint(
    "replays",
    __name__,
    static_folder=archive.File.DIR.resolve(),
    url_prefix="/replays",
)

app.register_blueprint(custom)
app.register_blueprint(replay_files)


@app.context_processor
def inject_globals():
    return {"photon": photon}


@app.route("/")
def index():
    return flask.render_template("dashboard.html.j2")


@app.get("/<int:id>/")
def status(id):
    client = photon.get_client(id)
    if not client:
        return flask.abort(400)
    return {"active": client.status}


@app.get("/<int:id>/preview")
def preview(id):
    return flask.render_template(
        "preview.html.j2", client=photon.get_client(id)
    )


@app.get("/<int:id>/preview/frame")
def get_preview_frame(id):
    client: photon.Client = photon.get_client(id)
    if not client:
        return flask.abort(400)
    source = (
        client.client.get_current_program_scene().current_program_scene_name
    )
    encoded_base64_image = client.client.get_source_screenshot(
        source, "jpeg", None, None, None
    ).image_data
    return encoded_base64_image


@app.post("/<int:id>/export")
def export(id):
    client: photon.Client = photon.get_client(id)
    if not client:
        return flask.abort(400)
    client.client.save_replay_buffer()
    replay_path = (
        client.client.get_last_replay_buffer_replay().saved_replay_path
    )
    audit.log(f"Exported replay {replay_path} from {client.name}")
    return OK


@app.post("/<int:id>/wake")
def wake(id):
    client: photon.Client = photon.clients[id]
    client.start()
    return {
        "success": client.client is not None,
    }


@app.get("/replays")
def replays():
    files = archive.get_files()
    return flask.render_template("replays.html.j2", files=files)
