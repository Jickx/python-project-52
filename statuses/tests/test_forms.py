from django.test import TestCase
from statuses.forms import StatusForm
from statuses.models import Status


class StatusFormTests(TestCase):
    def test_valid_data(self):
        form = StatusForm(data={'name': 'Open'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_required_name(self):
        form = StatusForm(data={'name': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_name_max_length(self):
        max_len = Status._meta.get_field('name').max_length
        too_long = 'x' * (max_len + 1)
        form = StatusForm(data={'name': too_long})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_unique_name(self):
        Status.objects.create(name='Unique')
        form = StatusForm(data={'name': 'Unique'})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_errors_shape(self):
        form = StatusForm(data={'name': ''})
        self.assertFalse(form.is_valid())
        # Errors is a dict-like with lists per field
        self.assertIsInstance(form.errors, dict)
        self.assertIsInstance(form.errors.get('name'), list)

