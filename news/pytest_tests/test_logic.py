import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    """
    Проверяем, что аноним не может создать коммент
    """
    comments_count_before = Comment.objects.count()
    news_url = reverse('news:detail', args=(news.id,))
    client.post(news_url, data=form_data)
    assert Comment.objects.count() == comments_count_before


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news, form_data):
    """
    Проверяем, что авторизованный пользователь может создать коммент
    """
    comments_count_before = Comment.objects.count()
    news_url = reverse('news:detail', args=(news.id,))
    response = author_client.post(news_url, data=form_data)
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() > comments_count_before
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news,):
    """
    Проверяем на запрещенные слова
    """
    comments_count_before = Comment.objects.count()
    news_url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Текст, {BAD_WORDS[0]}, и еще текст'}
    response = author_client.post(news_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == comments_count_before


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, news, comment):
    """
    Проверяем, что автор может удалить свой коммент
    """
    comments_count_before = Comment.objects.count()
    delete_url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    response = author_client.delete(delete_url)
    assertRedirects(response, f'{news_url}#comments')
    assert Comment.objects.count() < comments_count_before


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    """
    Проеряем, что нельзя удалить чужой коммент
    """
    comments_count_before = Comment.objects.count()
    delete_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_before


def test_author_can_edit_comment(author_client, form_data, news, comment):
    """
    Проверяем, что автор может редактировать свой коммент
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, f'{news_url}#comments')
    # Обновляет форму и добавляет записи в БД
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        admin_client,
        form_data,
        comment):
    """
    Проеряем, что нельзя редактировать чужой коммент
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
