from django.conf.urls import url, include
from . import views
from .controllers import search

urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^search/(?P<param>[\w]+)/', include([
        url(r'^$', search.index),
        url(r'^(?P<pageno>[0-9]{,3})/$', search.index),
    ]), name='search'),
]
