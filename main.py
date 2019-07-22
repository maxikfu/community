from flask import Flask, request
import json
import vk
import auth
import re
import scrap
import storage
from datetime import datetime
import bot_akinator
import requests


auth = auth.Token()
app = Flask(__name__)
aki_keyboard_en = json.dumps(
    {
        "one_time": True,
        "buttons":
            [
                [
                    {
                        "action":
                            {
                                "type": "text",
                                "label": "Yes"
                            },
                        "color": "positive"
                    },
                    {
                        "action":
                            {
                                "type": "text",
                                "label": "No"
                            },
                        "color": "negative"
                    },
                    {
                        "action":
                            {
                                "type": "text",
                                "label": "I don't know"
                            },
                        "color": "primary"
                    },
                    {
                        "action":
                            {
                                "type": "text",
                                "label": "Back"
                            },
                        "color": "negative"
                    }
                ],
                [
                    {
                        "action":
                            {
                                "type": "text",
                                "label": "Probably"
                            },
                        "color": "primary"
                    },
                    {
                        "action":
                            {
                                "type": "text",
                                "label": "Probably Not"
                            },
                        "color": "primary"
                    },
                    {
                        "action":
                            {
                                "type": "text",
                                "label": "Stop"
                            },
                        "color": "secondary"
                    }
                ]


            ]
    }
)
welcome_keyboard = json.dumps(
    {
        "one_time": True,
        "buttons":
            [
                [
                    {
                        "action":
                            {
                                "type": "text",
                                "label": "Akinator"
                            },
                        "color": "positive"
                    }
                ]

            ]
    }
)


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
        text = data['object']['text']
        att_photo = ""
        keyboard = welcome_keyboard
        playing = str(user_id) in storage.coll_content(bot_akinator.AKINATOR_COLLECTION)
        # user want to play game with akinator
        if re.search(r"Akinator", text, re.IGNORECASE) or playing:
            response = bot_akinator.game(user_id, text, datetime.now(), playing)
            message_template = response['text']
            # not sending game keyboard if game ended
            if response['win']:
                keyboard = welcome_keyboard
            else:
                keyboard = aki_keyboard_en
            # uploading image if exists
            if response['image_url']:
                destination = api.photos.getMessagesUploadServer(peer_id=user_id)
                image_get = requests.get(response['image_url'], stream=True)
                # converting to multipart format, name of image doesn't matter
                image_data = ("image.jpg", image_get.raw, image_get.headers['Content-Type'])
                # sending files to server and getting photo id, owner_id etc
                meta = requests.post(destination['upload_url'], files={'photo': image_data}).json()
                photo = api.photos.saveMessagesPhoto(photo=meta['photo'], server=meta['server'], hash=meta['hash'])
                # attachment need to be in special format
                att_photo = 'photo' + str(photo[0]['owner_id']) + "_" + str(photo[0]['id'])
        else:
            message_template = 'Ваше сообщение перенаправлено администратору, '\
                               'он свяжется с вами в скором времени, а пока Вы можете поиграть в Акинатора! Спасибо!'
        api.messages.send(peer_id=user_id, message=message_template, random_id=data['object']['random_id'],
                          attachment=att_photo, keyboard=keyboard)
        return 'ok'
    # new wall post handler
    elif data['type'] == 'wall_post_new':
        if data['object']['from_id'] != auth.comm_id:
            session = vk.Session(access_token=auth.user)
            api = vk.API(session, v=5.95)
            api.wall.post(owner_id=auth.comm_id, from_group=1, signed=anonymity_check(data['object']['text']),
                          post_id=data['object']['id'])
        return 'ok'
    # user joined the group
    elif data['type'] == 'group_join':
        session = vk.Session(access_token=auth.community)
        api = vk.API(session, v=5.95)
        user_id = data['object']['user_id']
        message_template = 'Спасибо что вы присоединились к нашему сообществу.\n' \
                           'Чтобы опубликовать новость на стене анонимно, необходимо в сообщение указать слово ' \
                           'Анон либо Анонимно, в противном случае анонимность поста не гарантирована. ' \
                           'Вы так же можете поиграть в Акинатор!'
        api.messages.send(peer_id=user_id, message=message_template, random_id=0, keyboard=welcome_keyboard)
        return 'ok'
    # user left the group
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
        last = storage.get(u'db', u'news')['threshold']
        for article in scrap.get_news():
            if article['datetime'] > last:
                response = scrap.post(auth, article, api)
                if response != 'error':
                    # here we update last posted news date in the file
                    last = article['datetime']
        storage.update(u'db', u'news', {u'threshold': last})
    return 'ok'


@app.route('/cleaning_fb', methods=['POST', 'GET'])
def cleaning_fb():
    if request.headers['X-Appengine-Cron']:
        # here we check how long passed after last message to akinator
        # if it is long enough delete the document from collection
        docs = storage.coll_content(bot_akinator.AKINATOR_COLLECTION)
        for doc in docs:
            get_doc = storage.get(bot_akinator.AKINATOR_COLLECTION, doc)
            # if more than 5 min passed we delete aki history
            if (datetime.now() - get_doc['last_active']).seconds > 300:
                storage.delete(bot_akinator.AKINATOR_COLLECTION, doc)
    return 'ok'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081, debug=True)
    # session = vk.Session(access_token=auth.community)
    # api = vk.API(session, v=5.101)
    # user_id = 491551942
    # message_template = 'Спасибо что вы присоединились к нашему сообществу.\n' \
    #                    'Чтобы опубликовать новость на стене анонимно, необходимо в сообщение указать слово ' \
    #                    'Анон либо Анонимно, в противном случае анонимность поста не гарантирована.'
    # args = {"peer_id": user_id, "message": message_template, "random_id": 0, "keyboard": aki_keyboard_en}
    # api.messages.send(**args)

