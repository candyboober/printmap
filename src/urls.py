# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns
from . import views


urlpatterns = patterns(
    '',
    url(r'^$', views.PrintLayView.as_view(), name='print_lay'),
)
