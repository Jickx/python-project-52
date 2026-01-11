from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.contrib.messages.constants import SUCCESS, ERROR
from django.db.models import ProtectedError
from unittest.mock import patch

from statuses.models import Status

class StatusCRUDTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='pass12345')
        self.status1 = Status.objects.create(name='New')
        self.status2 = Status.objects.create(name='In progress')

    def test_list_requires_login(self):
        resp = self.client.get(reverse('statuses:list'))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('statuses:list')}")

    def test_list_authenticated(self):
        self.client.login(username='user', password='pass12345')
        resp = self.client.get(reverse('statuses:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'New')
        self.assertContains(resp, 'In progress')

    def test_create_requires_login(self):
        resp = self.client.get(reverse('statuses:create'))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('statuses:create')}")

    def test_create_post_success(self):
        self.client.login(username='user', password='pass12345')
        resp = self.client.post(reverse('statuses:create'), {'name': 'Testing'})
        self.assertRedirects(resp, reverse('statuses:list'))
        self.assertTrue(Status.objects.filter(name='Testing').exists())
        msgs = list(get_messages(resp.wsgi_request))
        self.assertTrue(any(m.level == SUCCESS for m in msgs))

    def test_update_requires_login(self):
        resp = self.client.get(reverse('statuses:update', args=[self.status1.id]))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('statuses:update', args=[self.status1.id])}")

    def test_update_post_success(self):
        self.client.login(username='user', password='pass12345')
        resp = self.client.post(reverse('statuses:update', args=[self.status1.id]), {'name': 'Updated'})
        self.assertRedirects(resp, reverse('statuses:list'))
        self.status1.refresh_from_db()
        self.assertEqual(self.status1.name, 'Updated')
        msgs = list(get_messages(resp.wsgi_request))
        self.assertTrue(any(m.level == SUCCESS for m in msgs))

    def test_delete_requires_login(self):
        resp = self.client.get(reverse('statuses:delete', args=[self.status2.id]))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('statuses:delete', args=[self.status2.id])}")

    def test_delete_post_success(self):
        self.client.login(username='user', password='pass12345')
        resp = self.client.post(reverse('statuses:delete', args=[self.status2.id]))
        self.assertRedirects(resp, reverse('statuses:list'))
        self.assertFalse(Status.objects.filter(id=self.status2.id).exists())
        msgs = list(get_messages(resp.wsgi_request))
        self.assertTrue(any(m.level == SUCCESS for m in msgs))

    def test_delete_protected_error(self):
        self.client.login(username='user', password='pass12345')
        with patch('statuses.views.Status.delete', side_effect=ProtectedError('protected', None)):
            resp = self.client.post(reverse('statuses:delete', args=[self.status1.id]))
        self.assertRedirects(resp, reverse('statuses:list'))
        self.status1.refresh_from_db()
        self.assertTrue(Status.objects.filter(id=self.status1.id).exists())
        msgs = list(get_messages(resp.wsgi_request))
        self.assertTrue(any(m.level == ERROR for m in msgs))

    def test_create_get_form(self):
        """Test that create view displays the form"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.get(reverse('statuses:create'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'name')
        self.assertTemplateUsed(resp, 'statuses/create.html')

    def test_update_get_form(self):
        """Test that update view displays the form with existing data"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.get(reverse('statuses:update', args=[self.status1.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.status1.name)
        self.assertTemplateUsed(resp, 'statuses/update.html')

    def test_delete_get_confirmation(self):
        """Test that delete view displays confirmation page"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.get(reverse('statuses:delete', args=[self.status1.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'statuses/delete.html')

    def test_create_post_requires_login(self):
        """Test that creating status without login redirects"""
        resp = self.client.post(reverse('statuses:create'), {'name': 'Test'})
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('statuses:create')}")
        self.assertFalse(Status.objects.filter(name='Test').exists())

    def test_update_post_requires_login(self):
        """Test that updating status without login redirects"""
        resp = self.client.post(reverse('statuses:update', args=[self.status1.id]), {'name': 'Test'})
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('statuses:update', args=[self.status1.id])}")

    def test_delete_post_requires_login(self):
        """Test that deleting status without login redirects"""
        resp = self.client.post(reverse('statuses:delete', args=[self.status1.id]))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('statuses:delete', args=[self.status1.id])}")

    def test_create_empty_name(self):
        """Test that creating status with empty name shows validation error"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.post(reverse('statuses:create'), {'name': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['form'].errors.get('name'))

    def test_create_duplicate_name(self):
        """Test that creating status with duplicate name shows validation error"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.post(reverse('statuses:create'), {'name': 'New'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['form'].errors.get('name'))

    def test_create_long_name(self):
        """Test that creating status with name exceeding max_length shows error"""
        self.client.login(username='user', password='pass12345')
        long_name = 'a' * 256
        resp = self.client.post(reverse('statuses:create'), {'name': long_name})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['form'].errors.get('name'))

    def test_update_empty_name(self):
        """Test that updating status with empty name shows validation error"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.post(reverse('statuses:update', args=[self.status1.id]), {'name': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['form'].errors.get('name'))

    def test_update_duplicate_name(self):
        """Test that updating status with another status name shows validation error"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.post(reverse('statuses:update', args=[self.status1.id]), {'name': 'In progress'})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['form'].errors.get('name'))

    def test_update_nonexistent_status(self):
        """Test that updating non-existent status returns 404"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.get(reverse('statuses:update', args=[99999]))
        self.assertEqual(resp.status_code, 404)

    def test_delete_nonexistent_status(self):
        """Test that deleting non-existent status returns 404"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.get(reverse('statuses:delete', args=[99999]))
        self.assertEqual(resp.status_code, 404)

    def test_list_ordering(self):
        """Test that statuses are ordered by name"""
        self.client.login(username='user', password='pass12345')
        Status.objects.create(name='Zebra')
        Status.objects.create(name='Alpha')
        resp = self.client.get(reverse('statuses:list'))
        statuses = list(resp.context['statuses'])
        names = [s.name for s in statuses]
        self.assertEqual(names, sorted(names))

    def test_list_context_and_template(self):
        """Test that list view uses correct context and template"""
        self.client.login(username='user', password='pass12345')
        resp = self.client.get(reverse('statuses:list'))
        self.assertIn('statuses', resp.context)
        self.assertTemplateUsed(resp, 'statuses/list.html')
        self.assertEqual(len(resp.context['statuses']), 2)
