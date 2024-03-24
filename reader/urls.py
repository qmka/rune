from django.urls import path
from .views import index, get_board, get_feed, get_article, update_feeds

urlpatterns = [
    path('', index, name='index'),
    path('update_feeds/', update_feeds, name='init_feeds'),
    path('<slug:board_slug>/', get_board, name='get_board'),
    path('<slug:board_slug>/<slug:feed_slug>/', get_feed, name='get_feed'),
    path('<slug:board_slug>/<slug:feed_slug>/<slug:article_slug>/', get_article, name='get_article')
]
