from flask import Flask, request
import json

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def processing():
    data = json.loads(request.data)
    if 'type' not in data.keys:
        return 'not from vk'
    if data['type'] == 'confirmation':
        return '85b0d4a5'
    else:
        return 'ok'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)