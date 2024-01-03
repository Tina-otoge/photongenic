import datetime
import multiprocessing
from pathlib import Path

import flask
from flask import Blueprint, Flask

import archive
import photon

OK = flask.Response(status=200)

app = Flask(__name__)
app.config["APPLICATION_ROOT"] = photon.config.get("base_uri")
custom = Blueprint("custom", __name__, static_folder="../custom")
archive_files = Blueprint(
    "archive", __name__, static_folder=archive.File.DIR, url_prefix="/archive"
)

app.register_blueprint(custom)
app.register_blueprint(archive_files)

multiprocessing.Process(target=archive.generate_thumbnails).start()


@app.context_processor
def inject_globals():
    return {"photon": photon}


@app.route("/")
def index():
    return flask.render_template("dashboard.html.j2")


@app.get("/<int:id>/")
def status(id):
    client: photon.Client = photon.clients[id]
    return client.status


@app.get("/<int:id>/preview")
def preview(id):
    return flask.render_template("preview.html.j2", client=photon.clients[id])


@app.get("/<int:id>/preview/frame")
def get_preview_frame(id):
    client: photon.Client = photon.clients[id]
    source = (
        client.client.get_current_program_scene().current_program_scene_name
    )
    encoded_base64_image = client.client.get_source_screenshot(
        source, "png", None, None, None
    ).image_data
    return encoded_base64_image


@app.post("/<int:id>/export")
def export(id):
    client: photon.Client = photon.clients[id]
    client.client.save_replay_buffer()
    replay_path = (
        client.client.get_last_replay_buffer_replay().saved_replay_path
    )
    src = Path(replay_path)
    return OK

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


@app.post("/<int:id>/wake")
def wake(id):
    client: photon.Client = photon.clients[id]
    client.start()
    return {
        "success": client.client is not None,
    }


@app.get("/archive")
def get_archive():
    files = archive.get_files()
    return flask.render_template("archive.html.j2", files=files)
