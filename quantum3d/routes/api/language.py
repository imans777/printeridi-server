from flask import request, Response, json, jsonify, abort

from quantum3d.routes import api_bp as app
from quantum3d.constants import LANGUAGE_FOLDER_FULL_PATH
from quantum3d.db import pdb
import os


@app.route('/language-list')
def languageList():
    """
    GETs available language list
    Response: {
        languages: string[] # without ext / just lang names
    }
    """
    return jsonify({'languages': getLanguageList()})


def getLanguageList():
    files = os.listdir(LANGUAGE_FOLDER_FULL_PATH)
    languagenames = ['en']  # default language
    for name in files:
        if os.path.isfile(os.path.join(LANGUAGE_FOLDER_FULL_PATH, name)) and str(name).endswith('.json'):
            languagenames.append(str(name).split('.')[0])
    return languagenames
