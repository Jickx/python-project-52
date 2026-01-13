from django.test import TestCase
from django.contrib.auth import get_user_model

from users.forms import UserRegistrationForm, UserUpdateForm


class UserRegistrationFormTests(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_valid_registration(self):
        form = UserRegistrationForm(data={
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe',
            'password1': 'Str0ngPassw0rd!',
            'password2': 'Str0ngPassw0rd!',
        })
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertTrue(self.User.objects.filter(pk=user.pk, username='johndoe').exists())
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')

    def test_required_fields(self):
        form = UserRegistrationForm(data={
            'first_name': '',
            'last_name': '',
            'username': '',
            'password1': '',
            'password2': '',
        })
        self.assertFalse(form.is_valid())
        for field in ('first_name', 'last_name', 'username', 'password1', 'password2'):
            self.assertIn(field, form.errors)

    def test_password_mismatch(self):
        form = UserRegistrationForm(data={
            'first_name': 'Jane',
            'last_name': 'Roe',
            'username': 'janeroe',
            'password1': 'Str0ngPassw0rd!',
            'password2': 'DifferentPass1!',
        })
        self.assertFalse(form.is_valid())
        # UserCreationForm attaches mismatch error to password2
        self.assertIn('password2', form.errors)

    def test_username_unique(self):
        self.User.objects.create_user(username='taken', password='pass12345')
        form = UserRegistrationForm(data={
            'first_name': 'A',
            'last_name': 'B',
            'username': 'taken',
            'password1': 'Str0ngPassw0rd!',
            'password2': 'Str0ngPassw0rd!',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_errors_shape(self):
        form = UserRegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIsInstance(form.errors, dict)


class UserUpdateFormTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.u1 = self.User.objects.create_user(username='u1', password='pass12345', first_name='F1', last_name='L1')
        self.u2 = self.User.objects.create_user(username='u2', password='pass12345', first_name='F2', last_name='L2')

    def test_valid_update(self):
        form = UserUpdateForm(
            data={'first_name': 'John', 'last_name': 'Doe', 'username': 'newname'},
            instance=self.u1,
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.username, 'newname')

    def test_required_fields(self):
        form = UserUpdateForm(data={'first_name': '', 'last_name': '', 'username': ''}, instance=self.u1)
        self.assertFalse(form.is_valid())
        for field in ('first_name', 'last_name', 'username'):
            self.assertIn(field, form.errors)

    def test_username_unique_conflict(self):
        # Try to set u1's username to u2's username -> invalid
        form = UserUpdateForm(data={'first_name': 'F', 'last_name': 'L', 'username': 'u2'}, instance=self.u1)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_username_can_remain_same_for_instance(self):
        # Keeping the same username should be valid
        form = UserUpdateForm(data={'first_name': 'F1', 'last_name': 'L1', 'username': 'u1'}, instance=self.u1)
        self.assertTrue(form.is_valid(), form.errors)

