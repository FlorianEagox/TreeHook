from flask import Flask
app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 80
    app.run(DEFAULT_HOST, DEFAULT_PORT)
