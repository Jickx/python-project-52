from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.test import TestCase

from statuses.models import Status
from tasks.models import Task

User = get_user_model()


class TaskModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='author', password='pass')
        cls.executor = User.objects.create_user(username='executor', password='pass')
        cls.status = Status.objects.create(name='Open')

    def test_str_returns_name(self):
        t = Task(name='Fix bug', description='', status=self.status, author=self.author)
        self.assertEqual(str(t), 'Fix bug')

    def test_name_required(self):
        t = Task(name='', description='', status=self.status, author=self.author)
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn('name', ctx.exception.message_dict)

    def test_name_max_length(self):
        max_len = Task._meta.get_field('name').max_length
        t = Task(name='x' * (max_len + 1), description='', status=self.status, author=self.author)
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn('name', ctx.exception.message_dict)

    def test_description_blank_allowed(self):
        t = Task(name='Feature', description='', status=self.status, author=self.author)
        t.full_clean()  # should not raise
        t.save()
        self.assertIsNotNone(t.pk)

    def test_executor_optional(self):
        t = Task(name='Doc', description='write', status=self.status, author=self.author, executor=None)
        t.full_clean()  # should not raise
        t.save()
        self.assertIsNone(t.executor)

    def test_required_relations(self):
        # Missing status
        t1 = Task(name='X', description='', status=None, author=self.author)
        with self.assertRaises(ValidationError) as ctx1:
            t1.full_clean()
        self.assertIn('status', ctx1.exception.message_dict)
        # Missing author
        t2 = Task(name='Y', description='', status=self.status, author=None)
        with self.assertRaises(ValidationError) as ctx2:
            t2.full_clean()
        self.assertIn('author', ctx2.exception.message_dict)

    def test_reverse_relationships(self):
        t = Task.objects.create(
            name='Issue',
            description='',
            status=self.status,
            author=self.author,
            executor=self.executor,
        )
        status_accessor = Task._meta.get_field('status').remote_field.get_accessor_name()
        author_accessor = Task._meta.get_field('author').remote_field.get_accessor_name()
        executor_accessor = Task._meta.get_field('executor').remote_field.get_accessor_name()
        self.assertIn(t, getattr(self.status, status_accessor).all())
        self.assertIn(t, getattr(self.author, author_accessor).all())
        self.assertIn(t, getattr(self.executor, executor_accessor).all())

    def test_protect_on_delete_relations(self):
        Task.objects.create(
            name='Keep',
            description='',
            status=self.status,
            author=self.author,
            executor=self.executor,
        )
        with self.assertRaises(ProtectedError):
            self.status.delete()
        with self.assertRaises(ProtectedError):
            self.author.delete()
        with self.assertRaises(ProtectedError):
            self.executor.delete()

    def test_created_at_auto_now_add(self):
        t = Task.objects.create(name='Timestamp', description='', status=self.status, author=self.author)
        self.assertIsNotNone(t.created_at)
