from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from http import HTTPStatus
from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='iva')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Описание группы')

    def setUp(self):
        """Создание автороа поста"""
        self.author_client = Client()
        """Создание неавторизованного клиента"""
        self.guest_client = Client()
        """Создание аторизованного пользователя"""
        self.authorized_client = Client()
        self.user = User.objects.create_user('root')
        """Авторизация пользователя и автора с помощью функции force_login"""
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(PostURLTests.user)

    def test_home_group_profile_post_id_url(self):
        """Страница '/, /group/slug, /profile/username, posts/post_id/'
        доступна любому пользователю."""
        response_url_code_200 = {
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
        }
        for response_urls in response_url_code_200:
            with self.subTest():
                response = self.guest_client.get(response_urls)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_posts_post_id_edit_url(self):
        """Страница /posts/post_id/edit/ доступна автору"""
        response = self.author_client.get(
            f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_create_url(self):
        """Страница /posts/create/ доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_unexisting_page(self):
        """Запрос на несуществующую страницу /unexisting/ вернёт ошибку 404"""
        responce = self.guest_client.get('/unexisting/')
        self.assertEqual(responce.status_code, HTTPStatus.NOT_FOUND)

    def test_templates_guest_urls(self):
        """Проверка шаблонов страниц '/, group/slug,
        profile/username, posts/post_id"""
        templates_url = {
            'posts/index.html': '/',
            'posts/group_list.html': f'/group/{self.group.slug}/',
            'posts/profile.html': f'/profile/{self.user.username}/',
            'posts/post_detail.html': f'/posts/{self.post.pk}/',
        }
        for template, address in templates_url.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_templates_authorized_url(self):
        """Проверка шаблонов страниц /create/, /posts/post_id/edit/"""
        URL_1 = 'posts/create_post.html'
        URL_2 = URL_1
        templates_url = {
            URL_1: f'/posts/{self.post.pk}/edit/',
            URL_2: '/create/',
        }
        for template, address in templates_url.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
