from flask import request, Response, json, jsonify, abort

from quantum3d.routes import api_bp as app
from .consts import LANGUAGE_FOLDER_FULL_PATH
from quantum3d.db import pdb
import os


@app.route('/language', methods=['GET', 'POST'])
def languageManip():
    """
    GETs the current language
    Response: {
      lang: string
    }

    POSTs a new language
    Request: {
      lang: string
    }
    """
    if request.method == 'GET':
        lang = pdb.get_key('lang')
        return jsonify({'lang': lang}), 200
    elif request.method == 'POST':
        lang = request.json['lang']
        if lang not in getLanguageList():
            abort(404)
        pdb.set_key('lang', lang)
        return Response(status=200)


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
