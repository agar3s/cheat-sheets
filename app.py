from flask import Flask
from flask.ext.pymongo import PyMongo
from flask import render_template

app = Flask(__name__)
mongo = PyMongo(app)

@app.route('/')
def index():
   return render_template('index.html')

app.debug = True

if __name__ == '__main__':
   app.run()
