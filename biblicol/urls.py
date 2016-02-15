from django.conf.urls import url, include
from . import views
from .controllers.search import Search
# from .controllers.loader import Loader

urlpatterns = [
    url(r'^$', views.index, name='index'),

    url(r'^search/(?P<param>[\w\d.:_-]+)/', include([
        url(r'^$', Search.index),
        url(r'^(?P<pageno>[0-9]{,3})/$', Search.index),
    ]), name='search'),

    # url(r'^books/dump', Loader.load_books_into_db, name='load_up_books'),
]
