import configparser
import json
import mimetypes
import os
import re

from flask import Flask, render_template
from werkzeug.security import safe_join

app = Flask(__name__)

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding="UTF-8")

base_dir = config.get('explorateur', 'base_dir', fallback='.')

exclude_paths = ['\..*', '__pycache__', '__init__\.py', 'venv', 'cover', 'metas.json']


@app.route("/", methods=['GET'])
def index():
    return render_template('explorateur.html')


@app.route('/list/', methods=['GET'])
def list_dir_base():
    return list_dir("")


@app.route('/list/<path:subpath>', methods=['GET'])
def list_dir(subpath):
    for e_path in exclude_paths:
        if re.match(e_path, subpath):
            return "Ressource not found.", 404

    search_path = safe_join(base_dir, subpath)

    if os.path.isdir(search_path):
        paths = os.scandir(search_path)

        metadatas = {}
        if os.path.exists(safe_join(search_path, 'metas.json')):
            file_metas = open(safe_join(search_path, 'metas.json'), 'r')
            metadatas = json.loads(file_metas.read())
            file_metas.close()

        files = []
        directories = []
        return_paths = {"directories": directories, "files": files, 'current_path': subpath}
        if '.' in metadatas:
            return_paths['metas'] = metadatas['.']

        for path in paths:
            exclude = False
            for e_path in exclude_paths:
                if re.match(e_path, path.name):
                    exclude = True
            if not exclude:
                infos = path.stat()
                file_obj = {'filename': path.name, 'last_modified': infos.st_mtime}
                if path.name in metadatas:
                    file_obj.update(metadatas[path.name])
                if os.path.isfile(safe_join(search_path, path.name)):
                    file_obj['download_url'] = safe_join('list', subpath, path.name)
                    type = mimetypes.guess_type(safe_join(search_path, path.name))
                    if type and type[0]:
                        file_obj['type'] = type[0]

                    files.append(file_obj)
                elif os.path.isdir(safe_join(search_path, path.name)):
                    directories.append(file_obj)
        return return_paths, 200
    elif os.path.isfile(search_path):
        type = mimetypes.guess_type(search_path)
        headers = {}
        if type:
            if type[0]:
                headers['Content-Type'] = type[0]
            if type[1]:
                headers['Content-Encoding'] = type[1]
        return open(search_path, 'rb').read(), 200, headers
    else:
        return "Ressource not found.", 404


if __name__ == '__main__':
    # get properties

    flaskHost = '0.0.0.0'
    # logging
    flaskPort = 8082
    flaskDebug = False

    # start debug flask server
    app.run(host=flaskHost, port=flaskPort, debug=flaskDebug)
