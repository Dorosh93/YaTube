from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст длинный',
        )

    def test_model_post_have_correct_object_name(self):
        """Проверяем, что у модели POST корректно работает __str__."""
        post_str = str(PostModelTest.post)
        self.assertEqual(post_str, 'Тестовый текст ')


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovyij-slag',
            description='Тестовое описание',
        )

    def test_model_group_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group_str = str(GroupModelTest.group)
        self.assertEqual(group_str, 'Тестовая группа')


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст длинный',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария поста',
        )

    def test_model_comment_have_correct_object_name(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment_str = str(CommentModelTest.comment)
        self.assertEqual(comment_str, 'Текст комментар')


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='user')
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.user,
        )

    def test_model_follow_have_correct_object_name(self):
        """Проверяем, что у модели Follow корректно работает __str__."""
        follow_str = str(FollowModelTest.follow)
        self.assertEqual(follow_str, 'user подписан на auth')
