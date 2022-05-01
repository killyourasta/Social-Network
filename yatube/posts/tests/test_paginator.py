from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User
from . import test_fixtures as fixt


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name',
                                              email='test@mail.ru',
                                              password='test_pass',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug2',
            description='Тестовое описание')
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse(fixt.INDEX_URL_NAME))
        self.assertEqual(len(response.context['page_obj']),
                         settings.PAGINATOR_POSTS_ONTO_PAGE)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse
                                   (fixt.INDEX_URL_NAME) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
