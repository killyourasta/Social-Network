import tempfile

from http import HTTPStatus
from xml.etree.ElementTree import Comment

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import Post
from ..models import Comment, Group, Post, User
from . import test_fixtures as fixt

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            description='Описание',
            slug='test-task'
        )

    def test_create_post_form(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок от автора HasNoName',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse(fixt.POST_CREATE_URL_NAME),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=self.user,
                group=self.group.id,
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_with_picture(self):
        test_post = Post.objects.order_by('-id').values()[0]
        test_image = test_post['image']
        SMALL_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        PLOADED_IMG = SimpleUploadedFile(name='small.gif',
                                         content=SMALL_GIF,
                                         content_type='image/gif'
                                         )
        form_data = {
            'text': 'Пост с картинкой',
            'group': self.group.id,
            'image': PLOADED_IMG
        }
        response = self.authorized_client.post(
            reverse(fixt.POST_CREATE_URL_NAME),
            data=form_data,
            follow=True,)
        test_post = Post.objects.order_by('-id').values()[0]
        test_image = test_post['image']
        self.assertEqual(test_image, f'posts/{PLOADED_IMG}')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_without_picture(self):
        post_count = Post.objects.count()
        SMALL_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b''
            b'\x0A\x00\x3B'
        )
        PLOADED_IMG = SimpleUploadedFile(name='small.gif',
                                         content=SMALL_GIF,
                                         content_type='image/gif'
                                         )
        form_data = {
            'text': 'Пост с картинкой',
            'group': self.group.id,
            'image': PLOADED_IMG
        }
        response = self.authorized_client.post(
            reverse(fixt.POST_CREATE_URL_NAME),
            data=form_data,
            follow=True,)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_comment_create_form(self):
        post_1 = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        form_data = {
            'text': 'Пост для теста',
            'author': self.user,
            'post': post_1,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post_1.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                author=self.user,
                post=post_1,
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
