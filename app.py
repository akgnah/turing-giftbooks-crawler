# -*- coding: utf-8 -*-
import os
import sys

from django.conf import settings

DEBUG = os.environ.get('DEBUG', 'on') == 'on'

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

BASE_DIR = os.path.dirname(__file__)

settings.configure(
    DEBUG=DEBUG,
    SECRET_KEY=SECRET_KEY,
    ALLOWED_HOSTS=ALLOWED_HOSTS,
    ROOT_URLCONF=__name__,
    MIDDLEWARE_CLASSES=(
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ),
    INSTALLED_APPS=(
        'django.contrib.staticfiles',
    ),
    TEMPLATES=(
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': (os.path.join(BASE_DIR, 'templates'), ),
        },
    ),
    STATICFILES_DIRS=(
        os.path.join(BASE_DIR, 'static'),
    ),
    STATIC_URL='/static/',
)


import json
import time
import turing
from math import ceil
from django.conf.urls import url
from django.core.wsgi import get_wsgi_application
from django.http import HttpResponse
from django.shortcuts import render


def books(request):
    context = {
        'time': int(time.time())
    }
    return render(request, 'books.html', context)


def api_books(request):
    page = int(request.GET.get('page', 1))
    sort = request.GET.get('sort', 'date')
    q = request.GET.get('q')
    if q:
        books, total = turing.search(q, page - 1, 20, sort)
    else:
        books, total = turing.get_books(page - 1, 20, sort)

    context = {
        'total': total,
        'end': ceil(total / 20),
        'results': books
    }
    return HttpResponse(json.dumps(context), content_type="application/json")


urlpatterns = (
    url(r'^books/?$', books, name='books'),
    url(r'^api/books/?$', api_books, name='api-books'),
)


application = get_wsgi_application()


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
