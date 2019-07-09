from flask import Flask, request
import json
import vk
import auth
import random


auth = auth.Token()
app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def processing():
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    elif data['type'] == 'message_new':
        session = vk.Session(access_token=auth.community)
        api = vk.API(session, v=5.95)
        user_id = data['object']['from_id']
        message_template = 'Привет. Разработка чат-бота в процессе.'
        api.messages.send(peer_id=user_id, message=message_template, random_id=random.randint)
        return 'ok'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)