from outpost.django.base.decorators import docstring_format
from rest_flex_fields.views import FlexFieldsMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from . import (
    models,
    serializers,
)
from .conf import settings


class PersonRoomViewSet(FlexFieldsMixin, ReadOnlyModelViewSet):
    queryset = models.PersonRoom.objects.all()
    serializer_class = serializers.PersonRoomSerializer
    permission_classes = (IsAuthenticated,)
