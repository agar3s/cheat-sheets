from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
   return 'Create your own Cheat Sheet online!'

if __name__ == '__main__':
   app.run()
