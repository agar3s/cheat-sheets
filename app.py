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
        #incomplete data
        errors = {}
        user['username'] = user['username'].strip().lower()
        if len(user['username']) == 0:
            errors['username'] = 'your username can\'t be blank'

        if len(user['password']) == 0:
            errors['password'] = 'you need a password '

        user_found = db.users.find_one({'username':user['username'], 'password':user['password']})

        #username or password incorrect
        if not user_found:
            errors['not_valid'] = 'username or password is not valid'
            return render_template('login.html', user = user, errors = errors)

        user = UserMixin()
        user.username = user_found['username']
        user.id = user_found['_id'].__str__()
        login_user(user)
        g.user = user
        return redirect(request.args.get("next") or url_for("index"))
    
    return render_template('login.html', user= {'username':'', 'password':''})


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
            errors['username'] = 'The user %s is already registered' % new_user['username']
        
        if len(errors) > 0:
            return render_template('register.html', new_user=new_user, errors=errors)

        db.users.save(new_user)

        user = UserMixin()
        user.username = new_user['username']
        user.id = new_user['_id'].__str__()
        login_user(user)

        return redirect(request.args.get("next") or url_for("index"))
    
    elif request.method == 'GET':
        return render_template('register.html', new_user= {'username':'', 'password':'', 'email':''})


@app.route('/')
def index():
    query = {'public': {'$ne':False}} if current_user.is_anonymous() else { '$or': [{'owner':current_user.username},{'public': {'$ne':False}}] }
    query_sheets = db.sheets.find(query, sort=[("_id", -1)])
    cheat_sheets = []
    for sheet in list(query_sheets):
        if not 'owner' in sheet:
            sheet['owner'] = 'unknow'
        cheat_sheets.append(sheet)

    return render_template('index.html', cheat_sheets=cheat_sheets)


@app.route('/new', methods=['POST', 'GET'])
@login_required
def create_sheet():
    if request.method == 'POST':
        cheat_sheet_pre = request.form.to_dict()
        cheat_sheet = {}
        cheat_sheet['name'] = cheat_sheet_pre['name']
        cheat_sheet['description'] = cheat_sheet_pre['description']
        cheat_sheet['public'] = 'public' in cheat_sheet_pre
        cheat_sheet['owner'] = current_user.username

        index = 1
        variables = {}
        while ('key%d' % index) in cheat_sheet_pre:
            variables[cheat_sheet_pre['key%d' % index]] = cheat_sheet_pre['value%d' % index]
            index += 1;
        cheat_sheet['variables'] = variables

        db.sheets.save(cheat_sheet)
        return redirect(url_for('view_sheet', owner=cheat_sheet['owner'], name=cheat_sheet['name']))

    return render_template('create.html')


@app.route('/view/<owner>/<name>')
def view_sheet(owner, name):
    sheet = db.sheets.find_one({'name':name, 'owner':owner})

    if not sheet or ('public' in sheet and not sheet['public'] and current_user.username != owner):
        #temporary old sheets migration
        if owner == 'unknow':
            sheet = db.sheets.find_one({'name':name, 'owner':{'$exists':False}})
            if sheet:
                if current_user.is_active():
                    sheet['public'] = True
                    sheet['owner'] = 'unknow'

                return render_template('view.html', sheet = sheet)
        #temporary ends

        return redirect(url_for('index'))

    return render_template('view.html', sheet = sheet)


@app.route('/edit/<owner>/<name>', methods=['POST', 'GET'])
@login_required
def edit_sheet(owner, name):
    sheet = db.sheets.find_one({'name':name, 'owner':owner})
    if not sheet or ('public' in sheet and not sheet['public'] and current_user.username != owner):
        #temporary old sheets migration
        if owner == 'unknow':
            sheet = db.sheets.find_one({'name':name, 'owner':{'$exists':False}})
            if sheet:
                if current_user.is_active():
                    sheet['public'] = True
                    sheet['owner'] = current_user.username

            else:
                return redirect(url_for('index'))
        else:
        #temporary ends
            return redirect(url_for('index'))

    if request.method == 'POST':
        cheat_sheet_pre = request.form.to_dict()
        cheat_sheet = {}
        #default inmutable values
        cheat_sheet['name'] = sheet['name']
        cheat_sheet['owner'] = sheet['owner']
        cheat_sheet['public'] = sheet['public'] if 'public' in sheet else True

        #changes
        cheat_sheet['description'] = cheat_sheet_pre['description']

        if current_user.username == sheet['owner']:
            cheat_sheet['public'] = 'public' in cheat_sheet_pre

        index = 1
        variables = {}
        while ('key%d' % index) in cheat_sheet_pre:
            variables[cheat_sheet_pre['key%d' % index]] = cheat_sheet_pre['value%d' % index]
            index += 1;
        cheat_sheet['variables'] = variables

        db.sheets.update({'name':name, 'owner':owner}, cheat_sheet)

        #temporary old sheet migration
        if owner == 'unknow':
            db.sheets.update({'name':name, 'owner':{'$exists':False}}, cheat_sheet)
        #temporary ends

        return redirect(url_for('view_sheet', owner=cheat_sheet['owner'], name=cheat_sheet['name']))

    return render_template('edit.html', sheet = sheet)


@app.route('/user/<owner>', methods=['GET'])
def user(owner):
    query = {'owner':owner} if current_user.is_active() and current_user.username == owner else {'owner':owner,'public': {'$ne':False}}
    cheat_sheets = db.sheets.find(query,sort=[("_id", -1)])

    return render_template('user.html',owner=owner, cheat_sheets=cheat_sheets)


app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)