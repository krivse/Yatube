from http import HTTPStatus
import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, Comment, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth_1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.author,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.author_client = Client()
        self.author_client.force_login(self.post.author)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        count = Post.objects.all().count()
        self.uploaded.name = 'new_image.gif'
        form_data = {
            'text': 'Текст тестового поста 2',
            'group': self.group.pk,
            'image': self.uploaded
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.post.author}
        ))
        self.assertEqual(Post.objects.count(), count + 1)
        new_post = Post.objects.order_by('pk').last()
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.pk, form_data['group'])
        self.assertEqual(new_post.image.name,
                         'posts/' + form_data['image'].name)

    def test_post_edit(self):
        count = Post.objects.all().count()
        form_data = {
            'text': 'Редактирование поста',
            'group': self.group.pk
        }
        self.author_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}),
            data=form_data
        )
        edited_post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(Post.objects.all().count(), count)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.pk, form_data['group'])

    def test_comment_create(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=({self.post.id})),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            text='Текст комментария',
            author=self.author).exists()
        )
