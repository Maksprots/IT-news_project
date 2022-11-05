import shutil

from django.test import Client, TestCase
from django.urls import reverse
from ..models import Post, Group, User
from ..forms import PostForm
from django.test import Client, TestCase, override_settings
from django.urls import reverse
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateEditTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='test_page_us')
        cls.group = Group.objects.create(title='тест группа',
                                         slug='test_sl',
                                         description='тест описание')

        cls.post = Post.objects.create(text='тестовый текст поста',
                                       author=cls.user,
                                       group=cls.group)

        cls.form = PostForm()

    def setUp(self) -> None:
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        kw = {'username': 'test_page_us'}
        post_count = Post.objects.count()
        form_data = {
            'text': 'tejxt',
            'image': self.uploaded
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
        self.assertTrue(Post.objects.filter(text='tejxt',
                                            image='posts/small.gif'))

    def test_correct_edit_post(self):
        small_gif_new = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=small_gif_new,
            content_type='image1/gif')
        form_data = {
            'text': 'тестовый посt',
            'image': uploaded
        }
        post_old_text = self.post.text
        self.auth_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data)
        post_new = Post.objects.get(pk=self.post.pk)
        self.assertNotEqual(post_old_text, post_new.text)
        self.assertEqual(post_new.image,'posts/small1.gif' )

