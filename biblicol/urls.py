from django.conf.urls import url, include
from . import views
from .controllers.search import Search

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^search/(?P<param>[\w\d.:_-]+)/', include([
        url(r'^$', Search.index),
        url(r'^(?P<pageno>[0-9]{,3})/$', Search.index),
    ]), name='search'),
]
