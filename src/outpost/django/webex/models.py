import logging

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from outpost.django.campusonline.models import Person

logger = logging.getLogger(__name__)


class PersonRoom(models.Model):
    id = models.OneToOneField(
        Person, primary_key=True, on_delete=models.DO_NOTHING, db_constraint=False
    )
    modified = models.DateTimeField()
    url = models.URLField()
    sip = models.EmailField()
    call_in = ArrayField(models.CharField(max_length=128), null=True)
