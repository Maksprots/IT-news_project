from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group

User = get_user_model()


class URLTests(TestCase):
    templates_url_names = {
        '/': 'posts/index.html',
        '/group/test_sl/': 'posts/group_list.html',
        '/profile/nonauth/': 'posts/profile.html',
        '/posts/1/': 'posts/post_detail.html',
    }

    private_templates_url_names = {
        '/posts/1/edit/': 'posts/create_post.html',
        '/create/': 'posts/create_post.html',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='nonauth')
        cls.post = Post.objects.create(text='тестовый текст поста',
                                       author=cls.user)
        Group.objects.create(title='тест группа',
                             slug='test_sl',
                             description='тест описание')

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client2 = Client()
        user2 = User.objects.create_user(username='noauth')
        self.auth_client.force_login(self.user)
        self.auth_client2.force_login(user2)

    def page_test(self, response, template):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

    def test_common_pages(self):
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.page_test(response, template)
                response = self.auth_client.get(address)
                self.page_test(response, template)

    def test_private_pages(self):
        dict_unpack = self.private_templates_url_names.items()
        for address, template in dict_unpack:
            with self.subTest(address=address):
                response = self.auth_client.get(address)
                self.page_test(response, template)
        response = self.auth_client2.get('/posts/1/edit/')
        self.assertRedirects(response, '/')
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_not_found_response(self):
        response = self.guest_client.get('/createddd/')
        self.assertEqual(response.status_code, 404)
