import pytest

from django.test.client import Client
from news.models import Comment, News


@pytest.fixture  # Создаем автора
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture  # Создаем анонима
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


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
    news = News.objects.create(
        title='Заголовок',
        text='Текст')
    return news


@pytest.fixture  # Создаем комментарий
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment
