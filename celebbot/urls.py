from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'^$', views.index, name="index"),
  url(r'^bot/add_twitter$', views.add_twitter, name="add_twitter"),
  url(r'^bot/add$', views.add_bot, name="add_bot"),
  url(r'^error$', views.error, name='error')
]
