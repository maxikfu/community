from flask import Flask, request
import json
import vk
import auth
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
        message_template = 'Привет. Разработка чат-бота в процессе. Thank you!'
        api.messages.send(peer_id=user_id, message=message_template, random_id=data['object']['random_id'])
        return 'ok'
    # new wall post handler
    elif data['type'] == 'wall_post_new':
        if data['object']['from_id'] != auth.comm_id:
            session = vk.Session(access_token=auth.user)
            api = vk.API(session, v=5.95)
            api.wall.post(owner_id=auth.comm_id, from_group=1, signed=anonymity_check(data['object']['text']), post_id=data['object']['id'])
            return 'ok'
    # user joined the group
    elif data['type'] == 'group_join':
        session = vk.Session(access_token=auth.community)
        api = vk.API(session, v=5.95)
        user_id = data['object']['user_id']
        message_template = 'Thank you, for joining our community.\n' \
                           'Чтобы опубликовать новость на стене анонимно, необходимо в сообщение указать слово ' \
                           'Анон либо Анонимно, в противном случае анонимность поста не гарантирована.'
        api.messages.send(peer_id=user_id, message=message_template, random_id=0)
        return 'ok'
    elif data['type'] == 'group_leave':
        session = vk.Session(access_token=auth.community)
        api = vk.API(session, v=5.95)
        user_id = data['object']['user_id']
        message_template = 'We are sorry to see you go. Have a good life =)'
        if data['object']['self'] == 1:
            api.messages.send(peer_id=user_id, message=message_template, random_id=0)
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
