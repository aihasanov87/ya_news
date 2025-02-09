import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News

HOME_URL = reverse('news:home')


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


@pytest.fixture  # Создаем много новостей
def many_news(client):
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
    response = client.get(HOME_URL)
    object_list = response.context['object_list']

    return object_list


@pytest.fixture  # Создаем много комментариев
def many_comments(news, not_author_client, client):
    now = timezone.now()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        comment = Comment.objects.create(
            news=news,
            author=not_author_client,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    response = client.get(reverse('news:detail', args=(news.id,)))
    return response


@pytest.fixture
def form_data():
    return {'text': 'Новый текст'}
