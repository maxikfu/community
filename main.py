from flask import Flask, request
import json

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def processing():
    return '85b0d4a5'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)