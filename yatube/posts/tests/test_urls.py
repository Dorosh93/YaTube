from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.user2 = User.objects.create_user(username='auth2')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.user2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovyij-slag',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст длинный',
        )

    def test_url_nonauthorization(self):
        """"Доступ страниц для неавторизированного пользователя"""
        pages_status = {
            '/': HTTPStatus.OK,
            '/group/testovyij-slag/': HTTPStatus.OK,
            '/profile/auth/': HTTPStatus.OK,
            '/posts/1/': HTTPStatus.OK,
            '/posts/2/': HTTPStatus.NOT_FOUND,
            '/create/': HTTPStatus.FOUND,
            '/posts/1/edit/': HTTPStatus.FOUND,
            '/posts/1/comment/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.FOUND,
            '/profile/auth/follow/': HTTPStatus.FOUND,
            '/profile/auth/unfollow/': HTTPStatus.FOUND,
        }
        for url, status in pages_status.items():
            with self.subTest(url=url):
                response = PostURLTest.guest_client.get(url)
                self.assertEqual(response.status_code, status)
        pages_redirect = {
            '/create/': '/auth/login/?next=/create/',
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/posts/1/comment/': '/auth/login/?next=/posts/1/comment/',
            '/follow/': '/auth/login/?next=/follow/',
            '/profile/auth/follow/': '/auth/login/?next=/profile/auth/follow/',
            '/profile/auth/unfollow/': (
                '/auth/login/?next=/profile/auth/unfollow/'),
        }
        for url, redirect in pages_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_url_author(self):
        """"Доступ для автора поста"""
        pages_status = {
            '/create/': HTTPStatus.OK,
            '/posts/1/edit/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
            '/profile/auth2/follow/': HTTPStatus.FOUND,
            '/profile/auth2/unfollow/': HTTPStatus.FOUND,
        }
        for url, status in pages_status.items():
            with self.subTest(url=url):
                response = PostURLTest.author_client.get(url)
                self.assertEqual(response.status_code, status)
        pages_redirect = {
            '/profile/auth2/follow/': '/profile/auth2/',
            '/profile/auth2/unfollow/': '/profile/auth2/',
        }
        for url, redirect in pages_redirect.items():
            with self.subTest(url=url):
                response = self.author_client.get(url, follow=True)
                self.assertRedirects(response, redirect)

    def test_url_not_author(self):
        """"Доступ к посту для другого пользователя"""
        response = self.not_author_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_names = {
            '/': 'posts/index.html',
            '/group/testovyij-slag/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/none/': 'core/404.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in pages_names.items():
            with self.subTest(url=url):
                response = PostURLTest.author_client.get(url)
                self.assertTemplateUsed(response, template)
