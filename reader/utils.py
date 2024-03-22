import re
import requests
import io

from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def download(url):
    try:
        headers = {'User-Agent': UserAgent().chrome}
        timeout = 5
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text

    except requests.exceptions.RequestException as e:
        return getattr(e.response, "status_code", 400)


def download_json(url):
    try:
        headers = {'User-Agent': UserAgent().chrome}
        timeout = 5
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.json()

    except requests.exceptions.RequestException as e:
        return getattr(e.response, "status_code", 400)


def safe_download(url):
    max_parsable_content_length = 15 * 1024 * 1024
    try:
        response = requests.get(
            url=url,
            timeout=5,
            headers={'User-Agent': UserAgent().chrome},
            stream=True  # the most important part — stream response to prevent loading everything into memory
        )
    except requests.exceptions.RequestException as e:
        return getattr(e.response, "status_code", 400)
    response.encoding = 'utf-8'
    html = io.StringIO()
    total_bytes = 0

    for chunk in response.iter_content(chunk_size=100 * 1024, decode_unicode=True):
        total_bytes += len(chunk)
        if total_bytes >= max_parsable_content_length:
            return ""  # reject too big pages
        html.write(chunk)

    return html.getvalue()


def check_file_size(url):
    try:
        headers = {'User-Agent': UserAgent().chrome}
        timeout = 5
        response = requests.head(
            url,
            headers=headers,
            timeout=timeout)
        response.raise_for_status()
        size = int(response.headers.get("content-length", 0))

        if size > 10 * 1024:  # 10 KB
            return True
        else:
            return False

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while retrieving file size: {e}")
        return False

def transform_telegram_url_to_web_url(url):
    channel_name = url.split("/")[-1]
    transformed_url = "https://t.me/s/" + channel_name + "/"
    return transformed_url


def extract_background_image_url(html):
    pattern = r"background-image:url\('(.+?)'\)"
    match = re.search(pattern, html)
    if match:
        return match.group(1)
    else:
        return ''


def get_first_sentence(html):
    html = re.sub(r'<br\s*/?>|<hr\s*/?>', '.', html)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator=' ')
    cleaned_text = re.sub(r'<.*?>', '', text)
    sentence_delimiters = ['.', '?', '!']
    first_sentence = cleaned_text
    for delimiter in sentence_delimiters:
        if delimiter in cleaned_text:
            first_sentence = cleaned_text.split(delimiter, 1)[0] + delimiter
            break
    first_sentence = first_sentence.rstrip('.').rstrip()

    return first_sentence.strip()


def truncate_string_by_dot(input_string):
    dot_index = input_string.find('.')
    if dot_index != -1:
        truncated_string = input_string[:dot_index]
    else:
        truncated_string = input_string
    return truncated_string
