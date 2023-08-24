from rest_flex_fields import FlexFieldsModelSerializer

from . import models


class PersonRoomSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = models.PersonRoom
        fields = (
            "id",
            "url",
            "sip",
            "call_in",
        )
