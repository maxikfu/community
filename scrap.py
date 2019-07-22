import requests
from bs4 import BeautifulSoup
from datetime import datetime
import vk
import auth
import pytz
utc = pytz.UTC

announcements_url = 'http://urmary.cap.ru/news?type=announcements'
site_url_ = 'http://urmary.cap.ru/news/?type=news'


def get_news(site_url='http://urmary.cap.ru/news/?type=news'):
    # getting page content
    try:
        page = requests.get(site_url)
    except ConnectionError("ConnectionError to off web site"):
        return []
    # parsing html
    soup = BeautifulSoup(page.content, 'html.parser')
    # looking for the news list
    try:
        div_container = soup.find('div', attrs={'class': 'news_list'})
        news_list_all = div_container.find_all('div', attrs={'class': 'item_news'})
    except AttributeError:
        return []
    # iterating over news from the end to post them in chronological order
    for news_list in reversed(news_list_all):
        news_datetime = news_list.find('div', attrs={'class': 'news-list_date'})
        news_datetime = news_datetime.find('span').text
        news_datetime = datetime.strptime(news_datetime, '%H:%M | %d.%m.%Y')
        details = news_list.find('a', attrs={'class': 'news-list_title'})
        title = details.text
        url = 'http://urmary.cap.ru/' + details['href']
        full_article = requests.get(url)
        soup = BeautifulSoup(full_article.content, 'html.parser')
        tag_image = soup.find('img', attrs={'class': 'map_img'})
        if tag_image:
            image_url = tag_image['src']
        else:
            image_url = False
        news_container = soup.find('div', attrs={'class': 'news_text'})
        p_tags = news_container.find_all('p')
        article_text = ''
        for tags in p_tags:
            article_text += tags.text + '\n'
        # now we need to pass it to vk api
        d = {'image_url': image_url, 'title': title, 'text': article_text, 'datetime': utc.localize(news_datetime)}
        yield d


#  posting retrieved news on community wall
def post(auth, content, api):
    if content['image_url']:
        destination = api.photos.getWallUploadServer(group_id=auth.comm_id * (-1))
        image_get = requests.get(content['image_url'], stream=True)
        # converting to multipart format, name of image doesn't matter
        data = ("image.jpg", image_get.raw, image_get.headers['Content-Type'])
        # sending files to server and getting photo id, owner_id etc
        meta = requests.post(destination['upload_url'], files={'photo': data}).json()
        photo = api.photos.saveWallPhoto(group_id=auth.comm_id * (-1), photo=meta['photo'],
                                         server=meta['server'], hash=meta['hash'])
        # attachment need to be in special format
        att_photo = 'photo' + str(photo[0]['owner_id']) + "_" + str(photo[0]['id'])
    else:
        att_photo = None
    mess_template = content['title'] + '\n \n' + content['text'] + '\n Первоисточник: http://urmary.cap.ru'
    # posting to wall
    try:
        result = api.wall.post(owner_id=auth.comm_id, from_group=1, signed=0, message=mess_template, attachments=att_photo)
    except:
        result = 'error'
    return result


if __name__ == '__main__':
    pass


