from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms


from ..models import Post, Group, Follow

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('iva')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        """Создание автора поста"""
        self.user = User.objects.create_user('user')
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewsTests.user)

    def test_pages_templates_name(self):
        """Проверка всех шаблонов по name с помощью функции reverse"""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': f'{self.group.slug}'}):
                    'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}):
                    'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.pk}'}):
                    'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for name, template in templates_pages_names.items():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)

    def test_index_contex_view(self):
        """Проверка словаря context главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_objects = response.context['page_obj'][0]
        post_page_obj_0 = first_objects.text
        self.assertEqual(post_page_obj_0, PostViewsTests.post.text)

    def test_group_list_view(self):
        """Проверка словаря context для группы постов."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}))
        name_group = response.context['post']
        self.assertEqual(name_group.group, self.post.group)
        page_obg = response.context['page_obj'][0]
        self.assertEqual(page_obg.text, self.post.text)

    def test_profile_view(self):
        """Проверка словаря context для профиля с постами."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.post.author}'}))
        page_obj = response.context['page_obj'][0]
        self.assertEqual(page_obj.text, self.post.text)
        post = response.context['post']
        self.assertEqual(post.author, self.post.author)

    def test_post_detail_view(self):
        """Проверка словаря context с определённому посту."""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.pk}'}))
        name_group = response.context['post']
        self.assertEqual(name_group.group, self.post.group)

    def test_create_post_view(self):
        """Проверка context form для создания / редактирования поста."""
        templates = {
            'edit': reverse('posts:post_edit',
                            kwargs={'post_id': f'{self.post.pk}'}),
            'create': reverse('posts:post_create')
        }
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_field.items():
            for address in templates.values():
                response = self.authorized_client.get(address)
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_cash(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.content
        form_data = {
            'title': 'Тестовый заголовок',
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        response = self.authorized_client.get(reverse('posts:index'))
        second_object = response.content
        self.assertEqual(first_object, second_object)

    def test_follow_profile(self):
        follow_count = Follow.objects.count()
        Follow.objects.create(
            user=self.user,
            author=self.user
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='iva')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test_slug',
        )
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post.objects.create(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=cls.group))

    def setUp(self):
        self.user = User.objects.create_user(username='User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        urls_names = {
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile',
                    kwargs={'username': 'iva'})}
        for test_url in urls_names:
            response = self.client.get(test_url)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_first_page_contains_three_records(self):
        urls_names = {
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile',
                    kwargs={'username': 'iva'})}
        for test_url in urls_names:
            response = self.client.get(test_url + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
