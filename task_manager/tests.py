from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from statuses.models import Status
from tasks.models import Task

class TasksURLsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(username='author', password='pass12345')
        self.executor = User.objects.create_user(username='executor', password='pass12345')
        self.status = Status.objects.create(name='New')
        self.task = Task.objects.create(
            name='Initial',
            description='Desc',
            status=self.status,
            author=self.author,
            executor=self.executor,
        )

    def test_list_requires_login(self):
        resp = self.client.get(reverse('tasks:list'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_list_authenticated(self):
        self.client.login(username='author', password='pass12345')
        resp = self.client.get(reverse('tasks:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('tasks', resp.context)

    def test_create_get_requires_login(self):
        resp = self.client.get(reverse('tasks:create'))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_create_get_authenticated(self):
        self.client.login(username='author', password='pass12345')
        resp = self.client.get(reverse('tasks:create'))
        self.assertEqual(resp.status_code, 200)

    def test_create_post_authenticated(self):
        self.client.login(username='author', password='pass12345')
        resp = self.client.post(reverse('tasks:create'), {
            'name': 'Task A',
            'description': 'Lorem',
            'status': self.status.id,
            'executor': self.executor.id
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Task.objects.filter(name='Task A', author=self.author).exists())

    def test_update_get_requires_login(self):
        resp = self.client.get(reverse('tasks:update', args=[self.task.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_update_get_authenticated(self):
        self.client.login(username='author', password='pass12345')
        resp = self.client.get(reverse('tasks:update', args=[self.task.id]))
        self.assertEqual(resp.status_code, 200)

    def test_update_post_authenticated(self):
        self.client.login(username='author', password='pass12345')
        resp = self.client.post(reverse('tasks:update', args=[self.task.id]), {
            'name': 'Updated name',
            'description': 'Updated desc',
            'status': self.status.id,
            'executor': self.executor.id
        })
        self.assertEqual(resp.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Updated name')

    def test_delete_get_requires_login(self):
        resp = self.client.get(reverse('tasks:delete', args=[self.task.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_delete_get_authenticated(self):
        self.client.login(username='author', password='pass12345')
        resp = self.client.get(reverse('tasks:delete', args=[self.task.id]))
        self.assertEqual(resp.status_code, 200)

    def test_delete_post_authenticated(self):
        self.client.login(username='author', password='pass12345')
        resp = self.client.post(reverse('tasks:delete', args=[self.task.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_detail_requires_login(self):
        resp = self.client.get(reverse('tasks:detail', args=[self.task.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_detail_authenticated(self):
        self.client.login(username='author', password='pass12345')
        resp = self.client.get(reverse('tasks:detail', args=[self.task.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['task'].id, self.task.id)

