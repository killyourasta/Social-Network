import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User
from . import test_fixtures as fixt

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        cls.PLOADED_IMG = SimpleUploadedFile(name='small.gif',
                                             content=SMALL_GIF,
                                             content_type='image/gif'
                                             )
        cls.group = Group.objects.create(
            title='Заголовок тестовой задачи',
            description='Описание',
            slug='test-task'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.PLOADED_IMG
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_pages_uses_correct_template(self):
        cache.clear()
        templates_pages_names = {
            reverse(fixt.INDEX_URL_NAME): fixt.INDEX_TEMPLATE,
            reverse(fixt.GROUP_URL_NAME,
                    kwargs={fixt.GROUP_KWARGS: self.group.slug}):
            fixt.GROUP_TEMPLATE,
            reverse(fixt.PROFILE_URL_NAME,
                    kwargs={fixt.PROFILE_KWARGS: self.user.username}):
            fixt.PROFILE_TEMPLATE,
            reverse(fixt.POST_DETAIL_URL_NAME,
                    kwargs={fixt.POST_DETAIL_KWARGS: self.post.id}):
            fixt.POST_DETAIL_TEMPLATE,
            reverse(fixt.POST_EDIT_URL_NAME,
                    kwargs={fixt.POST_DETAIL_KWARGS: self.post.id}):
            fixt.CREATE_POST_TEMPLATE,
            reverse(fixt.POST_CREATE_URL_NAME): fixt.CREATE_POST_TEMPLATE,
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        cache.clear()
        response = (self.authorized_client.get(
            reverse(fixt.INDEX_URL_NAME)))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        author = first_object.author
        group = first_object.group
        image = first_object.image
        pub_date = first_object.pub_date
        self.assertEqual(text, self.post.text)
        self.assertEqual(author, self.user)
        self.assertEqual(group, self.post.group)
        self.assertEqual(pub_date, self.post.pub_date)
        self.assertEqual(image, self.post.image)

    def test_profile_page_show_correct_context(self):
        cache.clear()
        response = (self.authorized_client.get(
            reverse(fixt.PROFILE_URL_NAME,
                    kwargs={fixt.PROFILE_KWARGS: self.user.username})))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        author = response.context['author']
        image = first_object.image
        post_count = response.context['post_count']
        self.assertEqual(text, self.post.text)
        self.assertEqual(author, self.user)
        self.assertEqual(image, self.post.image)
        self.assertEqual(post_count, +1)

    def test_group_posts_page_show_correct_context(self):
        cache.clear()
        response = (self.authorized_client.get(
            reverse(fixt.GROUP_URL_NAME,
                    kwargs={fixt.GROUP_KWARGS: self.group.slug})))
        first_object = response.context['page_obj'][0]
        group = response.context['group']
        image = first_object.image
        self.assertEqual(group, self.post.group)
        self.assertEqual(image, self.post.image)

    def test_group_posts_page(self):
        cache.clear()
        post_1 = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        list = (reverse(fixt.PROFILE_URL_NAME,
                        kwargs={fixt.PROFILE_KWARGS: self.user.username}),
                reverse(fixt.GROUP_URL_NAME,
                        kwargs={fixt.GROUP_KWARGS: self.group.slug}),
                reverse(fixt.INDEX_URL_NAME),
                )
        for i in list:
            with self.subTest(i=i):
                response = self.authorized_client.get(i)
                self.assertEqual(post_1, response.context['page_obj'][0])
        self.assertTrue(post_1, self.post.group)

    def test_separate_group_posts_page(self):
        response = (self.authorized_client.get(
                    reverse(fixt.POST_DETAIL_URL_NAME,
                            kwargs={fixt.POST_DETAIL_KWARGS: self.post.id}))
                    )
        post_2 = response.context['post']
        self.assertEqual(post_2, self.post)

    def test_cache_index(self):
        cache.clear()
        response = (self.authorized_client.get(
            reverse(fixt.INDEX_URL_NAME)))
        posts = response.content
        Post.objects.create(
            text='test_new_post',
            author=self.user,
        )
        response_prev = (self.authorized_client.get(
            reverse(fixt.INDEX_URL_NAME)))
        prev_posts = response_prev.content
        self.assertEqual(prev_posts, posts)
        cache.clear()
        response_new = (self.authorized_client.get(
            reverse(fixt.INDEX_URL_NAME)))
        new_posts = response_new.content
        self.assertNotEqual(prev_posts, new_posts)

    def test_comment_create(self):
        test_post = Post.objects.order_by('-id')[0]
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Пост с комментарием',
            'author': self.user
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={fixt.POST_DETAIL_KWARGS: test_post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
