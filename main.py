from flask import Flask, request
import json
import vk
import auth
import re
import scrap
from datetime import datetime



auth = auth.Token()
app = Flask(__name__)


# all posts anonymous, only if specify they will be not anonymous
def anonymity_check(wall_post_text):   # need more sophisticated algorithm
    if re.search(r"(не *анон)|(не *от *анон)", wall_post_text, re.IGNORECASE):  # not anon
        return 1
    elif re.search(r"\b(анон)\b|\b(анонимно)\b|(аноним)|\b(anon)", wall_post_text, re.IGNORECASE):  # anon post
        return 0
    else:
        return 1


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
        message_template = 'Привет. Разработка чат-бота в процессе. Ваше сообщение перенаправлено администратору, ' \
                           'он свяжется с вами в скором времению Спасибо!'
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
        message_template = 'Спасибо что вы присоединились к нашему сообществу.\n' \
                           'Чтобы опубликовать новость на стене анонимно, необходимо в сообщение указать слово ' \
                           'Анон либо Анонимно, в противном случае анонимность поста не гарантирована.'
        api.messages.send(peer_id=user_id, message=message_template, random_id=0)
        return 'ok'
    elif data['type'] == 'group_leave':
        session = vk.Session(access_token=auth.community)
        api = vk.API(session, v=5.95)
        user_id = data['object']['user_id']
        message_template = 'Нам жаль что Вы покинули наше сообщество. Если Вас не затруднит отправьте нам отзыв =)'
        if data['object']['self'] == 1:
            api.messages.send(peer_id=user_id, message=message_template, random_id=0)
        return 'ok'


@app.route('/news', methods=['POST', 'GET'])
def processing_news():
    if request.headers['X-Appengine-Cron']:
        session = vk.Session(access_token=auth.user)
        api = vk.API(session, v=5.95)
        # retrieving last post date
        with open('last_news_date.txt', 'r') as f:
            last = datetime.strptime(f.readline(), '%Y-%m-%d %H:%M:%S')
        for article in scrap.get_news():
            if article['datetime'] > last:
                response = scrap.post(auth, article, api)
                if response != 'error':
                    # here we update last posted news date in the file
                    last = article['datetime']
            break
    # with open('last_news_date.txt', 'w') as f:
    #     f.write(str(last))
    return 'ok'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081, debug=True)
