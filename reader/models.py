import random
from datetime import datetime

from django.db import models
from django.utils.text import slugify


class Board(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=32, unique=True)

    def __str__(self):
        return self.title

    @staticmethod
    def add_board(title, slug):
        existing_board = Board.objects.filter(slug=slug).first()
        if existing_board:
            return existing_board
        else:
            new_board = Board.objects.create(
                title=title,
                slug=slug
            )
            return new_board

    @staticmethod
    def get_first_board():
        return Board.objects.order_by('title').first()

    @staticmethod
    def get_board_by_title(title):
        return Board.objects.filter(title=title).first()

    @staticmethod
    def get_board_by_slug(slug):
        return Board.objects.filter(slug=slug).first()


class Feed(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=32, unique=True)
    subtitle = models.TextField(blank=True)
    site_url = models.URLField()
    feed_url = models.URLField()
    updated = models.DateTimeField()
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    @staticmethod
    def add_feed(title, subtitle, site_url, feed_url, board):
        existing_feed = Feed.objects.filter(feed_url=feed_url).first()
        if existing_feed:
            return existing_feed
        else:
            slug = slugify(title)
            new_feed = Feed.objects.create(
                title=title,
                subtitle=subtitle,
                site_url=site_url,
                feed_url=feed_url,
                board=board,
                slug=slug,
                updated=datetime.now()
            )
            return new_feed

    @staticmethod
    def get_feed_by_id(feed_id):
        return Feed.objects.filter(id=feed_id).first()

    @staticmethod
    def get_feed_by_slug(slug):
        return Feed.objects.filter(slug=slug).first()

    @staticmethod
    def get_feed_by_url(url):
        return Feed.objects.filter(feed_url=url).first()

    @staticmethod
    def get_random_feed():
        all_feeds = Feed.objects.all()
        if not all_feeds:
            return None
        return random.choice(all_feeds)

    @staticmethod
    def get_first_feed():
        return Feed.objects.order_by('-updated')[0]

    @staticmethod
    def get_first_feed_by_board(board):
        return Feed.objects.filter(board=board).first()

    @staticmethod
    def get_feeds_by_board(board):
        return Feed.objects.filter(board=board).all()


class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=32, unique=True)
    description = models.TextField(blank=True)
    url = models.URLField()
    published = models.DateTimeField()
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True)
    is_read = models.BooleanField(default=False)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    @staticmethod
    def add_article(title, description, url, feed, published, thumbnail):
        feed = Feed.objects.get(pk=feed)
        slug = slugify(title)
        existing_article = Article.objects.filter(slug=slug).first()
        if existing_article:
            return existing_article
        else:
            new_article = Article.objects.create(
                title=title,
                slug=slug,
                description=description,
                url=url,
                feed=feed,
                published=published,
                thumbnail=thumbnail,
                is_read=False
            )
            return new_article

    @staticmethod
    def get_last_articles(feed, limit):
        if limit <= 0:
            return Article.objects.none()
        articles = Article.objects.filter(feed=feed).order_by('-published')[:limit]
        return articles

    @staticmethod
    def get_article_by_id(article_id):
        try:
            return Article.objects.get(pk=article_id)
        except Article.DoesNotExist:
            return None

    @staticmethod
    def get_article_by_slug(slug):
        try:
            return Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return None

    @staticmethod
    def set_article_as_read(article):
        if article:
            article.is_read = True
            article.save()
            return True
        return False

    @staticmethod
    def get_articles_by_feed(feed, limit=None):
        articles = Article.objects.filter(feed=feed).order_by('-published')
        if limit is not None:
            articles = articles[:limit]
        return articles
