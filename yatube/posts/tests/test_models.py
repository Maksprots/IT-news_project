from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тест группа',
            slug='слаг',
            description='сообщение тест',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для теста метода '
                 'str')

    def test_models_have_correct_object_names(self):
        str_name_post = 'Тестовый пост д'
        str_name_group = 'Тест группа'
        self.assertEqual(self.post.__str__(), str_name_post)
        self.assertEqual(self.group.__str__(), str_name_group)

    def test_fields_have_help_text_verbose_name(self):
        pass

    '''   text_help_text = 'Введите текст поста'
    group_verbose_name = 'Группа'
    group_help_text = 'Группа, к которой будет относиться пост'
    self.assertEqual(self._meta.get_field())'''