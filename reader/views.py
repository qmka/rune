import yaml

from django.shortcuts import render, redirect

from .models import Board, Feed, Article
from .parsers import get_rss, parse_rss, parse_tj, parse_kanobu, parse_telegram


FEED_LENGTH = 30

def index(request):
    boards = Board.objects.all()
    selected_board = Board.get_first_board()

    feeds = Feed.get_feeds_by_board(selected_board)
    selected_feed = Feed.get_first_feed_by_board(selected_board)

    articles = Article.get_articles_by_feed(selected_feed, limit=FEED_LENGTH)
    is_article_selected = False
    selected_article = None

    return render(
        request,
        'feed.html',
        context={
            'title': 'RUNE RSS READER',
            'selected_board': selected_board,
            'selected_feed': selected_feed,
            'selected_article': selected_article,
            'boards': boards,
            'feeds': feeds,
            'articles': articles,
            'is_article_selected': is_article_selected
        }
    )


def get_board(request, board_slug):
    boards = Board.objects.all()
    selected_board = Board.get_board_by_slug(board_slug)

    feeds = Feed.get_feeds_by_board(selected_board)
    selected_feed = Feed.get_first_feed_by_board(selected_board)

    articles = Article.get_articles_by_feed(selected_feed, limit=FEED_LENGTH)
    is_article_selected = False
    selected_article = None

    return render(
        request,
        'feed.html',
        context={
            'title': 'RUNE RSS READER',
            'selected_board': selected_board,
            'selected_feed': selected_feed,
            'selected_article': selected_article,
            'boards': boards,
            'feeds': feeds,
            'articles': articles,
            'is_article_selected': is_article_selected
        }
    )


def get_feed(request, board_slug, feed_slug):
    boards = Board.objects.all()
    selected_board = Board.get_board_by_slug(board_slug)

    feeds = Feed.get_feeds_by_board(selected_board)
    selected_feed = Feed.get_feed_by_slug(feed_slug)

    articles = Article.get_articles_by_feed(selected_feed, limit=FEED_LENGTH)
    is_article_selected = False
    selected_article = None

    return render(
        request,
        'feed.html',
        context={
            'title': 'RUNE RSS READER',
            'selected_board': selected_board,
            'selected_feed': selected_feed,
            'selected_article': selected_article,
            'boards': boards,
            'feeds': feeds,
            'articles': articles,
            'is_article_selected': is_article_selected
        }
    )


def get_article(request, board_slug, feed_slug, article_slug):
    boards = Board.objects.all()
    selected_board = Board.get_board_by_slug(board_slug)

    feeds = Feed.get_feeds_by_board(selected_board)
    selected_feed = Feed.get_feed_by_slug(feed_slug)

    articles = Article.get_articles_by_feed(selected_feed, limit=FEED_LENGTH)
    is_article_selected = True
    selected_article = Article.get_article_by_slug(article_slug)

    Article.set_article_as_read(selected_article)

    return render(
        request,
        'feed.html',
        context={
            'title': 'RUNE RSS READER',
            'selected_board': selected_board,
            'selected_feed': selected_feed,
            'selected_article': selected_article,
            'boards': boards,
            'feeds': feeds,
            'articles': articles,
            'is_article_selected': is_article_selected
        }
    )


def update_feeds(request):
    with open('boards/boards.yml', 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    boards = data['boards']
    for board in boards:
        Board.add_board(board['title'], board['slug'])
        for feed in board['feeds']:
            print(f"adding feed: {feed['title']}")
            if feed['type'] == 'RSS':
                raw_feed = get_rss(feed['url'])
                parse_rss(raw_feed, feed['title'], board['title'])
            elif feed['type'] == 'TJ':
                parse_tj(feed['url'], feed['title'], board['title'])
            elif feed['type'] == 'Telegram':
                parse_telegram(feed['url'], feed['title'], board['title'])
            elif feed['type'] == 'Kanobu':
                parse_kanobu(feed['url'], feed['site_url'], feed['title'], board['title'])
    print('DB updated!')
    return redirect('index')
