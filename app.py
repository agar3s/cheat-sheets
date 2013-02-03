import os
from urlparse import urlparse
from flask import Flask
from flask.ext.pymongo import PyMongo
from pymongo import Connection
from flask import render_template, request

app = Flask(__name__)

 
MONGO_URL = os.environ.get('MONGOHQ_URL')
 
if MONGO_URL:
# Get a connection
    connection = Connection(MONGO_URL)
# Get the database
    db = connection[urlparse(MONGO_URL).path[1:]]
else:
# Not on an app with the MongoHQ add-on, do some localhost action
    connection = Connection('localhost', 27017)
    db = connection['MyDB']


@app.route('/')
def index():
    return render_template('index.html', cheat_sheets=db.sheets.find(sort=[("_id", -1)]))


@app.route('/new', methods=['POST', 'GET'])
def create_sheet():
    if request.method == 'POST':
        cheat_sheet_pre = request.form.to_dict()
        cheat_sheet = {}
        cheat_sheet['name'] = cheat_sheet_pre['name'];

        index = 1
        variables = {}
        while ('key%d' % index) in cheat_sheet_pre:
            variables[cheat_sheet_pre['key%d' % index]] = cheat_sheet_pre['value%d' % index]
            index += 1;
        cheat_sheet['variables'] = variables

        print cheat_sheet
        db.sheets.save(cheat_sheet)

    return render_template('create.html')


@app.route('/view/<name>')
def view_sheet(name):
    sheet = db.sheets.find_one({'name':name})
    return render_template('view.html', sheet = sheet)

app.debug = True

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)