from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.conf import settings

from tasks.models import Task
from statuses.models import Status


class TaskViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(username='u1', password='pass12345')
        cls.other = User.objects.create_user(username='u2', password='pass12345')
        cls.status = Status.objects.create(name='New')
        cls.task = Task.objects.create(
            name='Task A',
            description='Desc A',
            status=cls.status,
            author=cls.user,
            executor=cls.other,
        )

    def setUp(self):
        self.client = Client()

    # Helpers
    def assert_login_redirect(self, response, target_path: str):
        login_url = reverse('login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(f'{login_url}?next={target_path}'))

    # Auth requirements
    def test_list_requires_login(self):
        url = reverse('tasks:list')
        resp = self.client.get(url)
        self.assert_login_redirect(resp, url)

    def test_detail_requires_login(self):
        url = reverse('tasks:detail', args=[self.task.pk])
        resp = self.client.get(url)
        self.assert_login_redirect(resp, url)

    def test_create_requires_login(self):
        url = reverse('tasks:create')
        resp = self.client.get(url)
        self.assert_login_redirect(resp, url)

    def test_update_requires_login(self):
        url = reverse('tasks:update', args=[self.task.pk])
        resp = self.client.get(url)
        self.assert_login_redirect(resp, url)

    def test_delete_requires_login(self):
        url = reverse('tasks:delete', args=[self.task.pk])
        resp = self.client.get(url)
        self.assert_login_redirect(resp, url)

    # GET views and context
    def test_list_get_ok_and_context(self):
        self.client.login(username='u1', password='pass12345')
        resp = self.client.get(reverse('tasks:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tasks/list.html')
        self.assertIn('tasks', resp.context)
        self.assertTrue(resp.context['tasks'].exists())

    def test_detail_get_ok_and_context(self):
        self.client.login(username='u1', password='pass12345')
        resp = self.client.get(reverse('tasks:detail', args=[self.task.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tasks/detail.html')
        self.assertIn('task', resp.context)
        self.assertEqual(resp.context['task'].pk, self.task.pk)

    def test_create_get_ok_and_form_context(self):
        self.client.login(username='u1', password='pass12345')
        resp = self.client.get(reverse('tasks:create'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tasks/create.html')
        form = resp.context.get('form')
        self.assertIsNotNone(form)
        for field in ('name', 'description', 'status', 'executor'):
            self.assertIn(field, form.fields)

    def test_update_get_ok_and_form_context(self):
        self.client.login(username='u1', password='pass12345')
        resp = self.client.get(reverse('tasks:update', args=[self.task.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tasks/update.html')
        form = resp.context.get('form')
        self.assertIsNotNone(form)
        for field in ('name', 'description', 'status', 'executor'):
            self.assertIn(field, form.fields)

    def test_delete_get_ok(self):
        self.client.login(username='u1', password='pass12345')
        resp = self.client.get(reverse('tasks:delete', args=[self.task.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'tasks/delete.html')

    # 404 for non-existent objects
    def test_detail_404(self):
        self.client.login(username='u1', password='pass12345')
        resp = self.client.get(reverse('tasks:detail', args=[999999]))
        self.assertEqual(resp.status_code, 404)

    def test_update_404(self):
        self.client.login(username='u1', password='pass12345')
        resp = self.client.get(reverse('tasks:update', args=[999999]))
        self.assertEqual(resp.status_code, 404)

    def test_delete_404(self):
        self.client.login(username='u1', password='pass12345')
        resp = self.client.get(reverse('tasks:delete', args=[999999]))
        self.assertEqual(resp.status_code, 404)

    # POST create/update/delete
    def test_create_post_success(self):
        self.client.login(username='u1', password='pass12345')
        url = reverse('tasks:create')
        payload = {
            'name': 'Task B',
            'description': 'Desc B',
            'status': self.status.pk,
            'executor': self.other.pk,
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('tasks:list'))
        created = Task.objects.get(name='Task B')
        self.assertEqual(created.author, self.user)
        self.assertEqual(created.executor, self.other)
        self.assertEqual(created.status, self.status)

    def test_update_post_success(self):
        self.client.login(username='u1', password='pass12345')
        url = reverse('tasks:update', args=[self.task.pk])
        payload = {
            'name': 'Task A (edited)',
            'description': 'Desc A edited',
            'status': self.status.pk,
            'executor': self.other.pk,
        }
        resp = self.client.post(url, data=payload)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('tasks:list'))
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Task A (edited)')
        self.assertEqual(self.task.description, 'Desc A edited')

    def test_delete_post_success(self):
        self.client.login(username='u1', password='pass12345')
        to_delete = Task.objects.create(
            name='Temp',
            description='Tmp',
            status=self.status,
            author=self.user,
            executor=self.other,
        )
        url = reverse('tasks:delete', args=[to_delete.pk])
        resp = self.client.post(url, data={})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('tasks:list'))
        self.assertFalse(Task.objects.filter(pk=to_delete.pk).exists())

    # Unsupported HTTP methods
    def test_put_is_not_allowed(self):
        self.client.login(username='u1', password='pass12345')
        # CreateView/UpdateView do not implement PUT -> 405
        resp_create = self.client.put(reverse('tasks:create'))
        resp_update = self.client.put(reverse('tasks:update', args=[self.task.pk]))
        self.assertEqual(resp_create.status_code, 405)
        self.assertEqual(resp_update.status_code, 405)

    def test_delete_http_method_is_not_allowed_on_deleteview(self):
        self.client.login(username='u1', password='pass12345')
        resp = self.client.delete(reverse('tasks:delete', args=[self.task.pk]))
        self.assertEqual(resp.status_code, 405)

    # Messages (language-agnostic: just check presence)
    def test_messages_on_create_update_delete(self):
        self.client.login(username='u1', password='pass12345')

        # Create
        resp1 = self.client.post(
            reverse('tasks:create'),
            data={
                'name': 'Msg C',
                'description': 'Msg C',
                'status': self.status.pk,
                'executor': self.other.pk,
            },
            follow=True,
        )
        msgs1 = list(get_messages(resp1.wsgi_request))
        self.assertTrue(len(msgs1) >= 1)

        # Update
        resp2 = self.client.post(
            reverse('tasks:update', args=[self.task.pk]),
            data={
                'name': 'Task A ++',
                'description': 'Desc ++',
                'status': self.status.pk,
                'executor': self.other.pk,
            },
            follow=True,
        )
        msgs2 = list(get_messages(resp2.wsgi_request))
        self.assertTrue(len(msgs2) >= 1)

        # Delete
        temp = Task.objects.create(
            name='To remove',
            description='X',
            status=self.status,
            author=self.user,
            executor=self.other,
        )
        resp3 = self.client.post(reverse('tasks:delete', args=[temp.pk]), follow=True)
        msgs3 = list(get_messages(resp3.wsgi_request))
        self.assertTrue(len(msgs3) >= 1)

