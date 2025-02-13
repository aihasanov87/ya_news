import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_home')),
        (pytest.lazy_fixture('url_detail')),
        (pytest.lazy_fixture('url_login')),
        (pytest.lazy_fixture('url_logout')),
        (pytest.lazy_fixture('url_signup')),
    )
)
@pytest.mark.django_db
def test_pages_availability(client, url):
    """Тестируем доступность страниц для анонинов"""
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
    'url',
    (pytest.lazy_fixture('url_edit'),
     pytest.lazy_fixture('url_delete'),
     ),
)
@pytest.mark.django_db
def test_pages_availability_for_different_users(
        parametrized_client,
        url,
        expected_status
):
    """Тестируем удаление и редактирование разными авторами"""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_edit')),
        (pytest.lazy_fixture('url_delete')),
    )
)
@pytest.mark.django_db
def test_redirect_for_anonymous_client(client, url, url_login):
    """Тестируем редиректы"""
    expected_url = f'{url_login}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
