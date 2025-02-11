import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
        client,
        form_data,
        url_detail):
    """Проверяем, что аноним не может создать коммент"""
    client.post(url_detail, data=form_data)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(
        author_client,
        author,
        news,
        form_data,
        url_detail):
    """Проверяем, что авторизованный пользователь может создать коммент"""
    response = author_client.post(url_detail, data=form_data)
    assertRedirects(response, f'{url_detail}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.parametrize(
    'bad_word',
    BAD_WORDS
)
@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news, bad_word, url_detail):
    """Проверяем на запрещенные слова"""
    bad_words_data = {'text': f'Текст, {bad_word}, и еще текст'}
    response = author_client.post(url_detail, data=bad_words_data)
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
        url_detail,
        url_delete):
    """Проверяем, что автор может удалить свой коммент"""
    response = author_client.delete(url_delete)
    assertRedirects(response, f'{url_detail}#comments')
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        url_delete):
    """Проеряем, что нельзя удалить чужой коммент"""
    response = not_author_client.delete(url_delete)
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
    edit_url = url_edit
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, f'{url_detail}#comments')
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
    response = admin_client.post(url_edit, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_db = Comment.objects.get(pk=comment.id)
    assert comment.text == comment_db.text
    assert comment.author == author
    assert comment.news == news
