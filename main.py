from flask import Flask, request
import json
import vk
import auth
import random
import sys
import re


auth = auth.Token()
app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def processing():
    data = json.loads(request.data)
    if 'type' not in data.keys():
        return 'not vk'
    #  handler for new messages
    elif data['type'] == 'message_new':
        session = vk.Session(access_token=auth.community)
        api = vk.API(session, v=5.95)
        user_id = data['object']['from_id']
        message_template = 'Привет. Разработка чат-бота в процессе.'
        api.messages.send(peer_id=user_id, message=message_template, random_id=random.randint(0, sys.maxsize))
        return 'ok'
    # new wall post handler
    elif data['type'] == 'wall_post_new':
        session = vk.Session(access_token=auth.user)
        api = vk.API(session, v=5.95)
        api.wall.post(owner_id=auth.comm_id, from_group=1, signed=anonymity_check(data['object']['text']), post_id=data['object']['id'])
        return 'ok'


# all posts anonymous, only if specify they will be not anonymous
def anonymity_check(wall_post_text):   # need more sophisticated algorithm
    if re.search(r"(не *анон)|(не *от *анон)", wall_post_text, re.IGNORECASE):  # not anon
        return 1
    elif re.search(r"\b(анон)\b|\b(анонимно)\b|(аноним)|\b(anon)", wall_post_text, re.IGNORECASE):  # anon post
        return 0
    else:
        return 1


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
