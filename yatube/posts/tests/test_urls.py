from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User
from . import test_fixtures as fixt


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            description='Описание',
            slug='test-task'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.GROUP_URL = fixt.GROUP_URL.format(group_slug=cls.group.slug)
        cls.PROFILE_URL = fixt.PROFILE_URL.format(
            profile_username=cls.user.username)
        cls.CREATE_POST_URL = fixt.CREATE_POST_URL.format(post_pk=cls.post.pk)
        cls.POST_DETAIL_URL = fixt.POST_DETAIL_URL.format(post_pk=cls.post.pk)

    def test_urls_uses_correct_template(self):
        cache.clear()
        url_templates_logged_in = {
            fixt.INDEX_URL: fixt.INDEX_TEMPLATE,
            self.GROUP_URL: fixt.GROUP_TEMPLATE,
            self.PROFILE_URL: fixt.PROFILE_TEMPLATE,
            self.POST_DETAIL_URL: fixt.POST_DETAIL_TEMPLATE,
            self.CREATE_POST_URL: fixt.CREATE_POST_TEMPLATE,
            fixt.POST_CREATE_URL: fixt.CREATE_POST_TEMPLATE,
            fixt.FAILURE_404_URL: fixt.FAILURE_404_TEMPLATE,
        }
        for address, template in url_templates_logged_in.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_url(self):
        response = self.client.get('unexists/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
