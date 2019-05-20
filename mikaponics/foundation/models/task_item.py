# -*- coding: utf-8 -*-
import csv
import pytz
from datetime import date, datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.indexes import BrinIndex
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class TaskItemManager(models.Manager):
    def full_text_search(self, keyword):
        """Function performs full text search of various textfields."""
        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        return TaskItem.objects.annotate(
            search=SearchVector('title', 'description',),
        ).filter(search=keyword)

    def delete_all(self):
        for obj in TaskItem.objects.iterator(chunk_size=500):
            obj.delete()


class TaskItem(models.Model):
    class Meta:
        app_label = 'foundation'
        db_table = 'mika_task_items'
        ordering = ['due_date']
        verbose_name = _('Task Item')
        verbose_name_plural = _('Task Items')
        default_permissions = ()
        permissions = ()
        indexes = (
            BrinIndex(
                fields=['due_date', 'created_at', 'last_modified_at',],
                autosummarize=True,
            ),
        )
        index_together = (
            ('user', 'created_at', 'is_closed'),
        )

    objects = TaskItemManager()
    id = models.BigAutoField(
        _("ID"),
        primary_key=True,
    )

    #
    #  FIELDS
    #

    user = models.ForeignKey(
        'User',
        help_text=_('The user whom this task belongs to.'),
        related_name="task_items",
        on_delete=models.CASCADE,
        blank=False,
        null=False
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_('The unique slug used for this task item when accessing details page.'),
        max_length=127,
        blank=True,
        null=False,
        db_index=True,
        unique=True,
        editable=False,
    )
    type_of = models.PositiveSmallIntegerField(
        _("Type of"),
        help_text=_('The type of task item this is.'),
    )
    title = models.CharField(
        _("Title"),
        max_length=63,
        help_text=_('The title this task item.'),
    )
    description = models.TextField(
        _("Description"),
        help_text=_('A short description of this task item.'),
    )
    due_date = models.DateField(
        _('Due Date'),
        help_text=_('The date that this task must be finished by.'),
        blank=True,
        null=True,
    )
    is_closed = models.BooleanField(
        _("Is Closed"),
        help_text=_('Was this task closed or is it still running?'),
        default=False,
        blank=True,
    )
    link = models.URLField(
        _("Link"),
        help_text=_('Link to the resource pertaining to this task item.'),
        null=True,
        blank=True
    )
    is_external_link = models.BooleanField(
        _("Is External Link"),
        help_text=_('Indicates if the link is external to the site or not.'),
        default=False,
        blank=True,
    )

    #
    #  SYSTEM FIELDS
    #

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    created_by = models.ForeignKey(
        'User',
        help_text=_('The user whom created this task item.'),
        related_name="created_task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    created_from = models.GenericIPAddressField(
        _("Created from"),
        help_text=_('The IP address of the creator.'),
        blank=True,
        null=True
    )
    created_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is creator a public IP and is routable.'),
        default=False,
        blank=True
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(
        'User',
        help_text=_('The user whom last modified this task item.'),
        related_name="last_modified_task_items",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    last_modified_from = models.GenericIPAddressField(
        _("Last modified from"),
        help_text=_('The IP address of the modifier.'),
        blank=True,
        null=True
    )
    last_modified_from_is_public = models.BooleanField(
        _("Is the IP "),
        help_text=_('Is modifier a public IP and is routable.'),
        default=False,
        blank=True
    )

    #
    #  FUNCTIONS
    #

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        """
        Override the save function so we can add extra functionality.

        (1) If we created the object then we will generate a custom slug.
        (a) If user exists then generate slug based on user's name.
        (b) Else generate slug with random string.
        """
        if not self.slug:
            count = TaskItem.objects.filter(user=self.user).count()
            count += 1

            # Generate our slug.
            self.slug = slugify(self.user)+"-task-"+str(count)

            # If a unique slug was not found then we will keep searching
            # through the various slugs until a unique slug is found.
            while TaskItem.objects.filter(slug=self.slug).exists():
                self.slug = slugify(self.user)+"-task-"+str(count)+"-"+get_random_string(length=8)

        super(TaskItem, self).save(*args, **kwargs)
