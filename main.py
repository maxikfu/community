from flask import Flask, request

app = Flask(__name__)
app.route('/')


def hello():
    return 'Hi'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)