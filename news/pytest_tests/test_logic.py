import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client,
        news,
        form_data,
        url_detail):
    """Проверяем, что аноним не может создать коммент"""
    news_url = reverse(url_detail, args=(news.id,))
    client.post(news_url, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        author_client,
        author,
        news,
        form_data,
        url_detail):
    """Проверяем, что авторизованный пользователь может создать коммент"""
    news_url = reverse(url_detail, args=(news.id,))
    response = author_client.post(news_url, data=form_data)
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize(
    'bad_word',
    (BAD_WORDS)
)
@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news, bad_word, url_detail):
    """Проверяем на запрещенные слова"""
    news_url = reverse(url_detail, args=(news.id,))
    bad_words_data = {'text': f'Текст, {bad_word}, и еще текст'}
    response = author_client.post(news_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(
        author_client,
        news,
        comment,
        url_detail,
        url_delete):
    """Проверяем, что автор может удалить свой коммент"""
    delete_url = reverse(url_delete, args=(comment.id,))
    news_url = reverse(url_detail, args=(news.id,))
    response = author_client.delete(delete_url)
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        comment,
        url_delete):
    """Проеряем, что нельзя удалить чужой коммент"""
    delete_url = reverse(url_delete, args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
        author_client,
        form_data,
        news,
        comment,
        author,
        url_detail,
        url_edit):
    """Проверяем, что автор может редактировать свой коммент"""
    edit_url = reverse(url_edit, args=(comment.id,))
    news_url = reverse(url_detail, args=(news.id,))
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, f'{news_url}#comments')
    # Обновляет форму и добавляет записи в БД
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        form_data,
        comment,
        author,
        news,
        url_edit):
    """Проеряем, что нельзя редактировать чужой коммент"""
    edit_url = reverse(url_edit, args=(comment.id,))
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_db = Comment.objects.get(pk=comment.id)
    assert comment.text == comment_db.text
    assert comment.author == author
    assert comment.news == news
