import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(many_news, client, url_home):
    """Тестируем кол-во новостей на главной странице"""
    response = client.get(reverse(url_home))
    object_list = response.context.get('object_list')
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(many_news):
    """Тестируем сортировку новостей от новых к старым"""
    object_list = many_news
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(author_client, news, url_detail, many_comments):
    """Тестируем сортировку комментариев от старых к новым"""
    response = author_client.get(reverse(url_detail, args=(news.id,)))
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news, url_detail):
    """Тестируем, что форма не доступна анониму"""
    news_url = reverse(url_detail, args=(news.id,))
    response = client.get(news_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news, url_detail):
    """Тестируем доступн формы для авторизованного пользователя"""
    news_url = reverse(url_detail, args=(news.id,))
    response = author_client.get(news_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
