import os
from urlparse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session, g
from flask.ext.pymongo import PyMongo
from pymongo import Connection
from bson.objectid import ObjectId
from flask_login import LoginManager, login_user, UserMixin, AnonymousUser, login_required, logout_user, current_user

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
    #get the user 3
    user_found = db.users.find_one({'_id': ObjectId(userid)})
    user = UserMixin()
    user.username = user_found['username']
    user.id = user_found['_id'].__str__()
    g.user = user
    return user


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        user = request.form.to_dict()

        #incomplete data
        if not 'username' in user or not 'password' in user:
            return redirect(url_for("login"))

        user_found = db.users.find_one({'username':user['username'], 'password':user['password']})

        #username or password incorrect
        if not user_found:
            return redirect(url_for("login"))

        user = UserMixin()
        user.username = user_found['username']
        user.id = user_found['_id'].__str__()
        login_user(user)
        g.user = user
        return redirect(request.args.get("next") or url_for("index"))
    
    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    g.user = None
    return redirect(url_for('index'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        new_user = request.form.to_dict()

        #incomplete data
        errors = {}
        new_user['username'] = new_user['username'].strip().lower()
        if len(new_user['username']) == 0:
            errors['username'] = 'your username can\'t be blank'

        if len(new_user['password']) == 0:
            errors['password'] = 'you need a password '

        #user already registered
        if db.users.find_one({'username':new_user['username']}):
            errors['used'] = 'The user %s is already registered, do you forget your password?' % new_user['username']
        
        if len(errors) > 0:
            return render_template('register.html', new_user=new_user, errors=errors)

        db.users.save(new_user)

        user = UserMixin()
        user.username = new_user['username']
        user.id = user_found['_id'].__str__()
        login_user(user)

        return redirect(request.args.get("next") or url_for("index"))
    
    elif request.method == 'GET':
        return render_template('register.html', new_user= {'username':'', 'password':'', 'email':''})


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