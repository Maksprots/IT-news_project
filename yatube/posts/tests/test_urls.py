from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group

User = get_user_model()
TEST_SLUG = 'test_sl'
POST_ID = 1
TEST_USERNAME = 'nonauth'


class URLTests(TestCase):
    templates_url_names = {
        '/': 'posts/index.html',
        f'/group/{TEST_SLUG}/': 'posts/group_list.html',
        f'/profile/{TEST_USERNAME}/': 'posts/profile.html',
        f'/posts/{POST_ID}/': 'posts/post_detail.html',
        '/about/author/': 'about/author.html',
        '/about/tech/': 'about/tech.html'
    }

    private_templates_url_names = {
        f'/posts/{POST_ID}/edit/': 'posts/create_post.html',
        '/create/': 'posts/create_post.html',
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.post = Post.objects.create(text='тестовый текст поста',
                                       author=cls.user)
        Group.objects.create(title='тест группа',
                             slug=TEST_SLUG,
                             description='тест описание')

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client2 = Client()
        user2 = User.objects.create_user(username='us_2')
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
        response = self.auth_client2.get(f'/posts/{POST_ID}/edit/')
        self.assertRedirects(response, '/')
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_not_found_response(self):
        response = self.guest_client.get('/createddd/')
        self.assertEqual(response.status_code, 404)
