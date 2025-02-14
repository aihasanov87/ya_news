from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture  # Создаем автора
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture  # Создаем анонима
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture  # Авторизуем автора
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture  # Авторизуем НЕ автора
def not_author_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture  # Создаем новость
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст')


@pytest.fixture  # Создаем комментарий
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture  # Создаем много новостей
def many_news():
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index))
        all_news.append(news)
    # Через метод bulk_create() создаем разом все записи
    News.objects.bulk_create(all_news)


@pytest.fixture  # Создаем много комментариев
def many_comments(news, author):
    now = timezone.now()
    for index in range(21):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}


@pytest.fixture  # Описываем маршрут home
def url_home():
    return reverse('news:home')


@pytest.fixture  # Описываем маршрут detail
def url_detail(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture  # Описываем маршрут delete
def url_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture  # Описываем маршрут edit
def url_edit(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture  # Описываем маршрут login
def url_login():
    return reverse('users:login')


@pytest.fixture  # Описываем маршрут logout
def url_logout():
    return reverse('users:logout')


@pytest.fixture  # Описываем маршрут signup
def url_signup():
    return reverse('users:signup')
