from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
import json
import os
from werkzeug.utils import secure_filename

bp = Blueprint('urlshort', __name__)


@bp.route('/')
def home():
    return render_template('home.html', codes=session.keys())


@bp.route('/your-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':
        urls = {}
        if os.path.exists('./urls.json'):
            with open('./urls.json', 'r') as urls_file:
                urls = json.load(urls_file)

        if request.form['code'] in urls:
            flash('That shortened code is taken. Please pick something else and retry.')
            return redirect(url_for('urlshort.home'))

        if 'url' in request.form:
            urls[request.form['code']] = {'url': request.form['url']}
        else:
            f = request.files['file']
            full_name = request.form['code'] + secure_filename(f.filename)
            f.save("./static/user_files/{}".format(full_name))
            urls[request.form['code']] = {'file': full_name}

        with open('./urls.json', 'w') as url_file:
            json.dump(urls, url_file)
            session[request.form['code']] = True
        return render_template('your_url.html', code=request.form['code'])
    else:
        return redirect(url_for('urlshort.home'))


@bp.route('/<string:code>')
def redirect_to_url(code):
    if os.path.exists('./urls.json'):
        with open('./urls.json', 'r') as urls_file:
            urls = json.load(urls_file)
        if code in urls:
            if 'url' in urls[code]:
                return redirect(urls[code]['url'])
            else:
                return redirect(url_for('static', filename='user_files/{}'.format(urls[code]['file'])))
    return abort(404)


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@bp.route('/api')
def session_api():
    return jsonify(list(session.keys()))
