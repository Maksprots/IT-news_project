from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group, User
from ..forms import PostForm


class PostCreateEditTest(TestCase):
    @classmethod
    def setUpClass(cls):
        print('class')
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_page_us')
        cls.group = Group.objects.create(title='тест группа',
                                         slug='test_sl',
                                         description='тест описание')

        cls.post = Post.objects.create(text='тестовый текст поста',
                                       author=cls.user, group=cls.group)
        cls.form = PostForm()

    def setUp(self) -> None:
        print('staup')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_create_post(self):
        kw = {'username': 'test_page_us'}
        post_count = Post.objects.count()
        form_data = {
            'text': 'tejxt'
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        ps = Post.objects.count()
        self.assertRedirects(response,
                             reverse(
                                 'posts:profile',
                                 kwargs=kw))
        self.assertEqual(post_count + 1, ps)

    def test_edit_post(self):
        text = self.post.text
        y='ghdf'
        self.auth_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.id}),
            data={'text': 'новый текст'},
            follow=True)
        new = Post.objects.get(pk=self.post.pk)
        self.assertNotEqual(text, new.text)
        self.assertIsInstance(y, str)
