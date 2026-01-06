from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.utils.translation import gettext as _
from django.db.models import ProtectedError
from unittest.mock import patch


class UserCRUDTestCase(TestCase):
    """Test CRUD operations for users (C=Create/Register, R=Read/List, U=Update, D=Delete)"""

    def setUp(self):
        self.client = Client()
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass456',
            first_name='Another',
            last_name='User'
        )

    def test_user_list_view(self):
        """Test that user list page is accessible without authentication"""
        response = self.client.get(reverse('users:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser1')
        self.assertContains(response, 'testuser2')

    def test_user_create_get(self):
        """Test GET request to user registration page"""
        response = self.client.get(reverse('users:create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Registration'))

    def test_user_create_post_success(self):
        """Test successful user registration (CREATE)"""
        user_count_before = User.objects.count()
        response = self.client.post(reverse('users:create'), {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        })
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertRedirects(response, reverse('home'))

        # Check user is automatically logged in
        new_user = User.objects.get(username='newuser')
        self.assertEqual(int(self.client.session['_auth_user_id']), new_user.id)

        # Check success message
        messages = list(get_messages(response.wsgi_request))
        expected = _('User successfully registered').lower()
        self.assertTrue(any(expected in str(m).lower() for m in messages))

    def test_user_create_post_invalid(self):
        """Test registration with mismatched passwords"""
        user_count_before = User.objects.count()
        response = self.client.post(reverse('users:create'), {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'differentpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), user_count_before)

        # Новый синтаксис для Django 4.1+
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_user_update_get_own_profile(self):
        """Test GET request to update own profile"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('users:update', args=[self.user1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser1')

    def test_user_update_get_other_profile(self):
        """Test GET request to update other user's profile (should redirect)"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('users:update', args=[self.user2.id]))
        self.assertRedirects(response, reverse('users:list'))
        messages = list(get_messages(response.wsgi_request))
        expected = _('You can only edit your own profile').lower()
        self.assertTrue(any(expected in str(m).lower() for m in messages))

    def test_user_update_post_success(self):
        """Test successful user profile update (UPDATE)"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.post(reverse('users:update', args=[self.user1.id]), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'username': 'testuser1',
        })
        self.assertRedirects(response, reverse('users:list'))

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Updated')
        self.assertEqual(self.user1.last_name, 'Name')

        messages = list(get_messages(response.wsgi_request))
        expected = _('User successfully updated').lower()
        self.assertTrue(any(expected in str(m).lower() for m in messages))

    def test_user_update_without_login(self):
        """Test update without authentication (should redirect to login)"""
        response = self.client.get(reverse('users:update', args=[self.user1.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('users:update', args=[self.user1.id])}")

    def test_user_delete_get_own_profile(self):
        """Test GET request to delete own profile confirmation page"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('users:delete', args=[self.user1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Are you sure'))

    def test_user_delete_get_other_profile(self):
        """Test GET request to delete other user's profile (should redirect)"""
        self.client.login(username='testuser1', password='testpass123')
        response = self.client.get(reverse('users:delete', args=[self.user2.id]))
        self.assertRedirects(response, reverse('users:list'))
        messages = list(get_messages(response.wsgi_request))
        expected = _('You can only delete your own profile').lower()
        self.assertTrue(any(expected in str(m).lower() for m in messages))

    def test_user_delete_post_success(self):
        """Test successful user deletion (DELETE)"""
        self.client.login(username='testuser1', password='testpass123')
        user_count_before = User.objects.count()
        response = self.client.post(reverse('users:delete', args=[self.user1.id]))

        self.assertEqual(User.objects.count(), user_count_before - 1)
        self.assertFalse(User.objects.filter(id=self.user1.id).exists())
        self.assertRedirects(response, reverse('users:list'))

        # Check user is logged out after deletion
        self.assertNotIn('_auth_user_id', self.client.session)

        messages = list(get_messages(response.wsgi_request))
        expected = _('User successfully deleted').lower()
        self.assertTrue(any(expected in str(m).lower() for m in messages))

    def test_user_delete_without_login(self):
        """Test delete without authentication (should redirect to login)"""
        response = self.client.get(reverse('users:delete', args=[self.user1.id]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('users:delete', args=[self.user1.id])}")

    def test_user_registration_duplicate_username(self):
        """Test registration with existing username"""
        response = self.client.post(reverse('users:create'), {
            'first_name': 'Duplicate',
            'last_name': 'User',
            'username': 'testuser1',  # Already exists
            'password1': 'complexpass123',
            'password2': 'complexpass123',
        })
        self.assertEqual(response.status_code, 200)

        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_user_delete_protected_error(self):
        """Test delete when related data protects the user (ProtectedError)"""
        self.client.login(username='testuser1', password='testpass123')
        with patch('users.views.User.delete', side_effect=ProtectedError('protected', None)):
            response = self.client.post(reverse('users:delete', args=[self.user1.id]))
        # Redirect to list
        self.assertRedirects(response, reverse('users:list'))
        # Error message is shown
        messages = list(get_messages(response.wsgi_request))
        expected = _('User cannot be deleted due to related data').lower()
        self.assertTrue(any(expected in str(m).lower() for m in messages))
        # User is logged out in finally block
        self.assertNotIn('_auth_user_id', self.client.session)

