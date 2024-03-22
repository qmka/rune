import feedparser
import json

from bs4 import BeautifulSoup
from datetime import datetime

from models import Feed, Article, Board
from utils import check_file_size, download, download_json, truncate_string_by_dot
from utils import transform_telegram_url_to_web_url, get_first_sentence, extract_background_image_url

TELEGRAM_CHANNEL_WEBVIEW_PREFIX = "https://t.me/s/"

TELEGRAM_MESSAGE_CLASS = ".tgme_widget_message"
TELEGRAM_MESSAGE_TEXT_CLASS = ".tgme_widget_message_text"
TELEGRAM_MESSAGE_PHOTO_CLASS = ".tgme_widget_message_photo_wrap"
TELEGRAM_MESSAGE_DATE_CLASS = ".tgme_widget_message_date"

DATETIME_PATTERNS = [
    '%Y-%m-%dT%H:%M:%S.%f',
    '%Y-%m-%dT%H:%M:%S',
    '%a, %d %b %Y %H:%M:%S %z'
    '%a, %d %b %Y %H:%M:%S %Z',
    '%d-%m-%y'
]


def get_rss(url):
    feed = feedparser.parse(url)
    return feed


def parse_rss(feed, feed_title, board_title):
    # add feed
    new_feed = Feed.add_feed(
        feed_title,
        feed.feed.subtitle,
        feed.feed.link,
        feed.href,
        Board.get_board_by_title(board_title)
    )

    # add feed articles
    for entry in feed.entries:
        soup = BeautifulSoup(entry.description, "html.parser")
        description = soup.get_text()
        thumbnail = get_thumbnail(entry)
        if 'published' in entry:
            published = convert_to_datetime(entry.published)
        else:
            published = datetime.now()
        Article.add_article(
            entry.title,
            description,
            entry.link,
            new_feed,
            published,
            thumbnail
        )


def get_thumbnail(entry):
    # searching for first large image
    # 1. searching in description
    if '<img' in entry.description:
        soup = BeautifulSoup(entry.description, 'html.parser')
        img_tag = soup.find('img')
        return img_tag.get('src')
    # 2. searching in content
    if 'content' in entry:
        # print(entry.content[0].value)
        soup = BeautifulSoup(entry.content[0].value, 'html.parser')
        img_tags = soup.find_all('img')

        # searching image that has size more that 10 kbytes in img tags
        for img_tag in img_tags:
            img_src = img_tag.get('src')
            if "data:" not in img_src and check_file_size(img_src):
                return img_src
    return ''


'''def convert_to_datetime(date_string):
    for pattern in DATETIME_PATTERNS:
        try:
            datetime_object = datetime.strptime(date_string, pattern)
            return datetime_object
        except ValueError:
            pass
    return None'''


def convert_to_datetime(date_string):
    datetime_format1 = '%a, %d %b %Y %H:%M:%S %z'
    datetime_format2 = '%a, %d %b %Y %H:%M:%S %Z'

    try:
        date = datetime.strptime(date_string, datetime_format1)
    except ValueError:
        try:
            date = datetime.strptime(date_string, datetime_format2)
        except ValueError:
            raise ValueError("Неверный формат даты")

    return date


def convert_to_datetime_tj(str_date):
    datetime_format = '%d-%m-%y'
    return datetime.strptime(str_date, datetime_format)


def convert_to_datetime_kanobu(str_date):
    # "%Y-%m-%dT%H:%M:%S.%f"
    datetime_format = '%Y-%m-%dT%H:%M:%S'
    return datetime.strptime(str_date, datetime_format)


def parse_kanobu(feed_url, site_url, feed_title, board_title):
    # https://www.igromania.ru/api/v3/articles/?limit=20
    # kanobu_data = get_kanobu_json(url)
    kanobu_data = download_json(feed_url)

    new_feed = Feed.add_feed(
        feed_title,
        '',
        site_url,
        feed_url,
        Board.get_board_by_title(board_title)
    )

    articles = kanobu_data['results']

    for article in articles:
        if 'desc' in article:
            article_description = article['desc']
        else:
            article_description = ''

        pubdate = truncate_string_by_dot(article['pubdate'])

        Article.add_article(
            article['title'],
            article_description,
            f"{site_url}{article['slug']}",
            new_feed,
            convert_to_datetime_kanobu(pubdate),
            article['pic']['origin'] or ''
        )


def parse_tj(url, feed_title, board_title):
    tj = get_tj_json(url)

    new_feed = Feed.add_feed(
        feed_title,
        tj['description'],
        url,
        url,
        Board.get_board_by_title(board_title)
    )

    for card in tj['cards']:
        article = card['article']
        article_url = f"{url[:-1]}{article['path']}"
        article_description = article['excerpt']
        if not card['media']['backgroundImage']:
            article_thumbnail = card['media']['image']['files']['original']['filepath']
        else:
            article_thumbnail = card['media']['backgroundImage']['files']['original']['filepath']

        Article.add_article(
            article['title'],
            article_description,
            article_url,
            new_feed,
            convert_to_datetime_tj(article['date_published']),
            article_thumbnail
        )


def get_kanobu_json(url):
    raw_content = download(url)
    soup = BeautifulSoup(raw_content, "html.parser")
    hidden_json_content = soup.find('script', {'type': 'application/json', 'id': '__NEXT_DATA__'})
    json_data = json.loads(hidden_json_content.string)

    with open('example_json.json', 'a', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False)

    return json_data


def get_tj_json(url):
    raw_content = download(url)
    soup = BeautifulSoup(raw_content, "html.parser")
    hidden_json_content = soup.find('script', {'type': 'application/json', 'data-id': 'flow-page'})
    json_data = json.loads(hidden_json_content.string)

    with open('example_json.json', 'a', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False)

    return json_data





def parse_telegram(url, channel_name, board_title, limit=100):
    web_url = transform_telegram_url_to_web_url(url)
    raw_content = download(web_url)

    with open('example.html', 'a', encoding='utf-8') as f:
        f.write(raw_content)

    soup = BeautifulSoup(raw_content, features="lxml")

    new_feed = Feed.add_feed(
        channel_name,
        '',
        url,
        url,
        Board.get_board_by_title(board_title)
    )

    message_tags = soup.select(TELEGRAM_MESSAGE_CLASS)
    counter = 1
    message_title = ''
    for message_tag in message_tags:
        message_html = message_tag.prettify()
        message_text = None
        message_text_tag = message_tag.select(TELEGRAM_MESSAGE_TEXT_CLASS)
        if message_text_tag:
            message_text = message_text_tag[0].decode_contents()
            message_title = get_first_sentence(message_text) or 'Без названия'

        message_photo = extract_background_image_url(message_html)

        message_url = None
        message_time = datetime.utcnow()
        message_date_tag = message_tag.select(TELEGRAM_MESSAGE_DATE_CLASS)
        if message_date_tag:
            message_url = message_date_tag[0]["href"]
            message_datetime_tag = message_date_tag[0].select("time")
            if message_datetime_tag:
                message_time = datetime.strptime(message_datetime_tag[0]["datetime"][:19], "%Y-%m-%dT%H:%M:%S")

        Article.add_article(
            message_title,
            message_text,
            message_url,
            new_feed,
            message_time,
            message_photo
        )

        counter += 1
        if counter > limit:
            break
