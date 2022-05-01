from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post, User
from . import test_fixtures as fixt


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.follower = User.objects.create_user(username='HName')
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            description='Описание',
            slug='test-task'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client.force_login(cls.follower)

    def test_follow_unfollow(self):
        follow_count = Follow.objects.count()
        response = (self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={fixt.PROFILE_KWARGS: self.user})))
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={fixt.PROFILE_KWARGS: self.user.username}
            )
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.user,
                user=self.follower,
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_new_post(self):
        Follow.objects.create(
            author=self.user,
            user=self.follower,
        )
        self.authorized_client.force_login(self.follower)
        response = (self.authorized_client.get(
            reverse(fixt.FOLLOW_INDEX_URL_NAME)))
        first_object = response.context['page_obj'][0]
        self.assertEqual(self.post, first_object)
        self.authorized_client.force_login(self.user)
        response = (self.authorized_client.get(
            reverse(fixt.FOLLOW_INDEX_URL_NAME)))
        with self.assertRaises(IndexError):
            response.context['page_obj'][0]
