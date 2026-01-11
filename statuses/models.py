from django.db import models
from django.utils.translation import gettext_lazy as _

class Status(models.Model):
    name = models.CharField(_('Name'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')
        ordering = ('name',)  # default ordering for lists

    def __str__(self):
        return self.name
