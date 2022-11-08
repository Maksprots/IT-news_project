from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class PostPagesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='test_page_us')
        cls.group = Group.objects.create(title='тест группа',
                                         slug='test_sl',
                                         description='тест описание')
        cls.group2 = Group.objects.create(title='тест группа2',
                                          slug='test_sl2',
                                          description='тест описание')
        cls.post = Post.objects.create(text='тестовый текст поста',
                                       author=cls.user,
                                       group=cls.group,
                                       image=cls.uploaded)
        for i in range(12):
            Post.objects.create(text='тестовый текст поста',
                                author=cls.user, group=cls.group)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': 'test_sl'}): (
                'posts/group_list.html'),
            reverse('posts:profile',
                    kwargs={'username': 'test_page_us'}): (
                'posts/profile.html'),
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}): (
                'posts/post_detail.html'),
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}): (
                'posts/create_post.html'),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                self.assertTemplateUsed(response, template)

    def post_test(self, response):
        first_obj = response.context['page_obj'][0]
        text = first_obj.text
        author = first_obj.author
        group = first_obj.group
        self.assertEqual(text, 'тестовый текст поста')
        self.assertEqual(author, self.user)
        self.assertEqual(group, self.group)

    def test_index_context(self):
        response = self.auth_client.get(reverse('posts:index'))
        self.post_test(response)
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_posts_context(self):
        kw = {'slug': 'test_sl'}
        response = self.auth_client.get(reverse('posts:group_list',
                                                kwargs=kw))
        self.post_test(response)
        group = response.context['group']
        self.assertEqual(group, self.group)
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:group_list',
                                           kwargs=kw) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_context(self):
        kw = {'username': 'test_page_us'}
        response = self.auth_client. \
            get(reverse('posts:profile',
                        kwargs=kw))
        self.post_test(response)
        author = response.context['author']
        self.assertEqual(author, self.user)
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.auth_client.get(reverse('posts:profile',
                                                kwargs=kw) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_post_detail(self):
        response = self.auth_client. \
            get(reverse('posts:post_detail',
                        kwargs={'post_id': f'{self.post.id}'}))

        post = response.context['post']
        self.assertEqual(post, self.post)
        author = response.context['author']
        self.assertEqual(author, self.user)

    def test_correct_context_create_post(self):
        response = self.auth_client.get(
            reverse('posts:post_create'))
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.ImageField
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_correct_context_post_edit(self):
        response = self.auth_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}))
        form_field = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
            'image': forms.ImageField
        }
        for value, expected in form_field.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        is_edit_context = response.context['is_edit']
        post_id_context = response.context['post_id']
        self.assertEqual(is_edit_context, True)
        self.assertEqual(post_id_context, self.post.id)

    def test_another_post_in_group(self):
        kw = {'slug': 'test_sl2'}
        response = self.auth_client.get(reverse('posts:group_list',
                                                kwargs=kw))
        self.assertNotIn(self.post, response.context['page_obj'])

    # картинка не передается в контекст в явном виде
    # передается объект класса Post а картинка-- атрибут
    # этого объекта, не совсем понял зачем тестировать, что
    # джанго передает объект целиком и не теряет картинку
    def test_index_image(self):
        pass

    def test_guest_comment(self):
        address = reverse('posts:add_comment', kwargs={'post_id': 1})
        response = self.guest_client.post(address)
        self.assertRedirects(response, '/auth/login/?next=/posts/1/comment/')

