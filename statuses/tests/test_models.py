from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from statuses.models import Status


class StatusModelTests(TestCase):
    def test_str_returns_name(self):
        s = Status(name='In progress')
        self.assertEqual(str(s), 'In progress')

    def test_name_is_required(self):
        s = Status(name='')
        with self.assertRaises(ValidationError) as ctx:
            s.full_clean()
        self.assertIn('name', ctx.exception.message_dict)

    def test_name_max_length(self):
        max_len = Status._meta.get_field('name').max_length
        s = Status(name='x' * (max_len + 1))
        with self.assertRaises(ValidationError) as ctx:
            s.full_clean()
        self.assertIn('name', ctx.exception.message_dict)

    def test_name_unique_validation_and_db_constraint(self):
        Status.objects.create(name='Open')
        dup = Status(name='Open')
        # Model-level unique validation
        with self.assertRaises(ValidationError) as ctx:
            dup.full_clean()
        self.assertIn('name', ctx.exception.message_dict)
        # DB-level unique constraint
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                dup.save()
