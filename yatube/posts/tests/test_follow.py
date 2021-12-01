from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.core.cache import cache
from django.urls import reverse
from ..models import Post, Follow

User = get_user_model()


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.user2 = User.objects.create_user(username='auth2')
        cls.author_client2 = Client()
        cls.author_client2.force_login(cls.user2)
        cls.user3 = User.objects.create_user(username='auth3')
        cls.author_client3 = Client()
        cls.author_client3.force_login(cls.user3)
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user2,
        )
        cls.follow2 = Follow.objects.create(
            user=cls.user2,
            author=cls.user3,
        )
        cls.post = Post.objects.create(
            author=cls.user2,
            text='Тестовый текст второго автора',
        )
        cls.post2 = Post.objects.create(
            author=cls.user3,
            text='Тестовый текст третьего автора',
        )

    def test_follow(self):
        cache.clear()
        post = Post.objects.create(
            author=FollowTest.user3,
            text='Тестовый текст нового поста',
        )
        response_user1 = FollowTest.author_client.get('/follow/').content
        self.assertNotIn(post.text, response_user1.decode())
        cache.clear()
        response_user2 = FollowTest.author_client2.get('/follow/').content
        self.assertIn(post.text, response_user2.decode())
        cache.clear()
        FollowTest.author_client.post(reverse(
            'posts:profile_follow', kwargs={'username': 'auth3'}))
        response2_user1 = FollowTest.author_client.get('/follow/').content
        self.assertIn(post.text, response2_user1.decode())
        cache.clear()
        FollowTest.author_client.post(reverse(
            'posts:profile_unfollow', kwargs={'username': 'auth3'}))
        response3_user1 = FollowTest.author_client.get('/follow/').content
        self.assertNotIn(post.text, response3_user1.decode())
