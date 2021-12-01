import shutil
import tempfile

from django.contrib.auth import get_user_model
from ..forms import CommentForm, PostForm
from ..models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.shortcuts import get_object_or_404
from django.urls import reverse

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreatePostTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovyij-slag',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст длинный',
        )
        cls.form = PostForm()
        cls.form_comm = CommentForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Создание поста из формы"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст длинный 2',
            'group': CreatePostTest.group.id,
            'image': uploaded,
        }
        response = CreatePostTest.author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': 'auth'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        """Изменение поста из формы"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый тестовый текст длинный',
            'group': CreatePostTest.group.id,
        }
        response = CreatePostTest.author.post(
            reverse('posts:post_edit', kwargs={'post_id': '1'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': '1'}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Новый тестовый текст длинный',
                group=1,
                id=1,
            ).exists()
        )

    def test_comment_add(self):
        post = get_object_or_404(Post, pk=1)
        comment_count = post.comments.count()
        comment_text = {
            'text': 'Комментарий',
        }
        response = CreatePostTest.author.post(
            reverse('posts:add_comment', kwargs={'post_id': '1'}),
            data=comment_text,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': '1'}))
        self.assertEqual(post.comments.count(), comment_count + 1)
