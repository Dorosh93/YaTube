import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from ..models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.user2 = User.objects.create_user(username='auth2')
        cls.author2_client = Client()
        cls.author2_client.force_login(cls.user2)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovyij-slag',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='testovyij-slag-2',
            description='Тестовое описание 2',
        )
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст первого поста',
            group=cls.group,
            image=uploaded
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста другой группы',
            group=cls.group_2,
        )
        cls.post = Post.objects.create(
            author=cls.user2,
            text='Тестовый текст поста другого автора без группы',
        )
        cls.comment = Comment.objects.create(
            post=get_object_or_404(Post, pk=1),
            author=cls.user,
            text='Комментарий',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'testovyij-slag'}): (
                'posts/group_list.html'),
            reverse('posts:profile', kwargs={'username': 'auth'}): (
                'posts/profile.html'),
            reverse('posts:post_detail', kwargs={'post_id': '1'}): (
                'posts/post_detail.html'),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}): (
                'posts/create_post.html'),
        }
        for reverse_name, template in pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostViewsTest.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def compare_post(self, post_choise, post_true):
        """Сравнение выбранного поста и правильного"""
        self.assertEqual(post_choise.text, post_true.text)
        self.assertEqual(post_choise.author, post_true.author)
        self.assertEqual(post_choise.group, post_true.group)
        self.assertEqual(post_choise.image, post_true.image)

    def test_first_page_index(self):
        """Cодержание 3-го поста на главной странице"""
        response = PostViewsTest.author_client.get(reverse('posts:index'))
        object_3 = response.context['page_obj'][2]
        post = get_object_or_404(Post, pk=1)
        self.compare_post(object_3, post)

    def test_first_page_group(self):
        """Содержание 1-го поста на странице группы"""
        response = PostViewsTest.author_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'testovyij-slag'}))
        object_1 = response.context['page_obj'][0]
        post = get_object_or_404(Post, pk=1)
        self.compare_post(object_1, post)

    def test_first_page_profile(self):
        """Cодержание 2-го поста на странице автора"""
        response = PostViewsTest.author_client.get(reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        object_1 = response.context['page_obj'][1]
        post_count = response.context['count_post']
        self.assertEqual(post_count, 2)
        post = get_object_or_404(Post, pk=1)
        self.assertEqual(object_1.comments, post.comments)
        self.compare_post(object_1, post)

    def test_page_detail_post(self):
        """Подробное описание 1-го поста"""
        response = PostViewsTest.author_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': '1'}))
        object_1 = response.context['post']
        post_count = response.context['count_post']
        post_title_1 = response.context['title_post']
        self.assertEqual(post_count, 2)
        self.assertEqual(post_title_1, 'Тестовый текст ')
        post = get_object_or_404(Post, pk=1)
        self.compare_post(object_1, post)

    def test_page_new_post(self):
        """Создание нового поста"""
        response = PostViewsTest.author_client.get(reverse(
            'posts:post_create'))
        object_new = response.context['form']
        post_text = object_new.instance.text
        post_group = str(object_new.instance.group)
        self.assertEqual(post_text, '')
        self.assertEqual(post_group, 'None')

    def test_page_post_edit(self):
        """Страница редактирования 2-го поста"""
        response = PostViewsTest.author_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': '2'}))
        object_2 = response.context['form']
        post_text_2 = object_2.instance.text
        post_group_2 = str(object_2.instance.group)
        post_is_edit = response.context['is_edit']
        post_post_id = response.context['post_id']
        self.assertEqual(post_text_2, 'Тестовый текст поста другой группы')
        self.assertEqual(post_group_2, 'Тестовая группа 2')
        self.assertEqual(post_is_edit, True)
        self.assertEqual(post_post_id, 2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='testovyij-slag',
            description='Тестовое описание',
        )
        for i in range(1, 12):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый текст {i} поста',
                group=cls.group,
            )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста без группы',
        )

    def test_second_page_index(self):
        """Количество постов на главной - 2 страница"""
        response = PaginatorViewsTest.author_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_second_page_group(self):
        """Количество постов на 2 странице группы"""
        response = PaginatorViewsTest.author_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'testovyij-slag'})
            + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 1)
