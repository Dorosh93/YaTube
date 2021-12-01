from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache
from ..models import Post

User = get_user_model()


class Test(TestCase):
    def test_cache(self):
        """Проверка работы cache"""
        user = User.objects.create_user(username='auth')
        author_client = Client()
        author_client.force_login(user)
        cache.clear()
        post = Post.objects.create(
            author=user,
            text='Тестовый текст',
        )
        author_client.get('/').content
        post.delete()
        response2 = author_client.get('/').content
        self.assertIn(post.text, response2.decode())
        cache.clear()
        response3 = author_client.get('/').content
        self.assertNotIn(post.text, response3.decode())
