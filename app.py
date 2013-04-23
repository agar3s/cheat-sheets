import os
from urlparse import urlparse
from flask import Flask
from flask.ext.pymongo import PyMongo
from pymongo import Connection
from flask import render_template, request, redirect, url_for
from flask_login import LoginManager, login_user

app = Flask(__name__)

# mongo configuration
MONGO_URL = os.environ.get('MONGOHQ_URL')
 
if MONGO_URL:
    connection = Connection(MONGO_URL)
    db = connection[urlparse(MONGO_URL).path[1:]]
else:
    connection = Connection('localhost', 27017)
    db = connection['MyDB']


#login manager
login_manager = LoginManager()
login_manager.setup_app(app)


@login_manager.user_loader
def load_user(userid):
    return {'username':userid,'name':'fulano'}


@app.route("/login", methods=["GET", "POST"])
def login():
    login_user({'username':userid,'name':'fulano'})
    return redirect(request.args.get("next") or url_for("index"))


@app.route('/')
def index():
    return render_template('index.html', cheat_sheets=db.sheets.find(sort=[("_id", -1)]))


@app.route('/new', methods=['POST', 'GET'])
def create_sheet():
    if request.method == 'POST':
        cheat_sheet_pre = request.form.to_dict()
        cheat_sheet = {}
        cheat_sheet['name'] = cheat_sheet_pre['name']
        cheat_sheet['description'] = cheat_sheet_pre['description']

        index = 1
        variables = {}
        while ('key%d' % index) in cheat_sheet_pre:
            variables[cheat_sheet_pre['key%d' % index]] = cheat_sheet_pre['value%d' % index]
            index += 1;
        cheat_sheet['variables'] = variables

        db.sheets.save(cheat_sheet)
        return redirect(url_for('view_sheet', name=cheat_sheet['name']))

    return render_template('create.html')


@app.route('/view/<name>')
def view_sheet(name):
    sheet = db.sheets.find_one({'name':name})
    if sheet:
        return render_template('view.html', sheet = sheet)
    
    return redirect(url_for('index'))


@app.route('/edit/<name>', methods=['POST', 'GET'])
def edit_sheet(name):
    sheet = db.sheets.find_one({'name':name})
    if not sheet:
        return redirect(url_for('index'))

    if request.method == 'POST':
        cheat_sheet_pre = request.form.to_dict()
        cheat_sheet = {}
        cheat_sheet['name'] = name
        cheat_sheet['description'] = cheat_sheet_pre['description']

        index = 1
        variables = {}
        while ('key%d' % index) in cheat_sheet_pre:
            variables[cheat_sheet_pre['key%d' % index]] = cheat_sheet_pre['value%d' % index]
            index += 1;
        cheat_sheet['variables'] = variables

        db.sheets.update({'name':name}, cheat_sheet)
        return redirect(url_for('view_sheet', name=name))

    return render_template('edit.html', sheet = sheet)
    


app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)