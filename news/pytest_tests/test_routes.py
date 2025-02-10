import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args',
    (
        (pytest.lazy_fixture('url_home'), None),
        (pytest.lazy_fixture('url_detail'), pytest.lazy_fixture('news')),
        (pytest.lazy_fixture('url_login'), None),
        (pytest.lazy_fixture('url_logout'), None),
        (pytest.lazy_fixture('url_signup'), None),
    )
)
@pytest.mark.django_db
def test_pages_availability(client, name, args, news):
    """Тестируем доступность страниц для анонинов"""
    if args:
        url = reverse(name, args=(args.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    (pytest.lazy_fixture('url_edit'),
     pytest.lazy_fixture('url_delete'),
     ),
)
@pytest.mark.django_db
def test_pages_availability_for_different_users(
        parametrized_client,
        name,
        comment,
        expected_status
):
    """Тестируем удаление и редактирование разными авторами"""
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        (pytest.lazy_fixture('url_edit'), pytest.lazy_fixture('comment')),
        (pytest.lazy_fixture('url_delete'), pytest.lazy_fixture('comment')),
    )
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, name, args, comment, url_login):
    """Тестируем редиректы"""
    login_url = reverse(url_login)
    url = reverse(name, args=(args.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
