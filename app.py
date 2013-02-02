from flask import Flask
from flask.ext.pymongo import PyMongo
from flask import render_template, request

app = Flask(__name__)

app.MONGO_DBNAME = 'cheats'
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html', cheat_sheets=mongo.db.sheets.find())

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
        mongo.db.sheets.save(cheat_sheet)

    return render_template('create.html')



app.debug = True

if __name__ == '__main__':
    app.run()
