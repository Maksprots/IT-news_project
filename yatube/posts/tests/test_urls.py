from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group

User = get_user_model()


class URLTests(TestCase):
    templates_url_names = {
        '/': 'posts/index.html',
        '/group/test_sl': 'posts/group_list.html',
        '/profile/HasNoName/': 'posts/profile.html',
        '/post/1/': 'posts/post_detail.html',
        '/post/1/edit/': 'posts/create_post.html',
        '/create/': 'posts/create_post.html',

    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='nonauth')
        Post.objects.create(text='тестовый текст поста',
                            author=cls.user)
        Group.objects.create(title='тест группа',
                             slug='test_sl',
                             description='тест описание')

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.auth_client.force_login(self.user)

    def test_homepage(self):

        response = self.guest_client.get('/group/test_sl/')
        self.assertEqual(response.status_code, 200)

