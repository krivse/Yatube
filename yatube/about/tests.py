from django.test import TestCase, Client
from http import HTTPStatus
from django.contrib.auth import get_user_model

User = get_user_model()


class StaticPagesURLTests(TestCase):
    def setUp(self):
        """Создание c авторизацией пользователя
        для тестирования сртраниц приложения about"""
        self.authorized_client = Client()
        self.user = User.objects.create_user('root')
        self.authorized_client.force_login(self.user)

    def test_about_author_url(self):
        """Страница /about/author/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_about_tech_url(self):
        """Страница /about/tech/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_templates_about_urls(self):
        """Проверка шаблонов страниц /about/author/, /about/tech/"""
        templates_url = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_url.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
