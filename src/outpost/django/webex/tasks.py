import json
import logging
from datetime import timedelta

import isodate
import phonenumbers
import requests
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from outpost.django.campusonline.models import Person
from purl import URL
from requests_oauthlib import OAuth2Session

from . import models
from .conf import settings

logger = logging.getLogger(__name__)


class Token:

    default = json.dumps(
        {
            "access_token": settings.WEBEX_ACCESS_TOKEN,
            "refresh_token": settings.WEBEX_REFRESH_TOKEN,
            "token_type": settings.WEBEX_TOKEN_TYPE,
            "expires_in": "-30",
        }
    )

    def __init__(self):
        self._token = json.loads(
            cache.get(settings.WEBEX_TOKEN_CACHE_KEY, self.default)
        )

    def get(self):
        return self._token

    def set(self, token):
        cache.set(settings.WEBEX_TOKEN_CACHE_KEY, json.dumps(token))
        self._token = token


class WebExTasks:
    @shared_task(bind=True, ignore_result=True, name=f"{__name__}.WebEx:person_room")
    def person_room(task):
        import pudb

        pu.db
        logging.info("Synchronizing personal room information")
        token = Token()
        base_url = URL(settings.WEBEX_BASE_URL)
        extra = {
            "client_id": settings.WEBEX_CLIENT_ID,
            "client_secret": settings.WEBEX_CLIENT_SECRET,
        }
        client = OAuth2Session(
            settings.WEBEX_CLIENT_ID,
            token=token.get(),
            auto_refresh_url=base_url.add_path_segment("access_token").as_string(),
            auto_refresh_kwargs=extra,
            token_updater=token.set,
        )
        total = Person.objects.count()
        for i, p in enumerate(Person.objects.all()):
            logger.debug(f"Updating {p}")
            url = base_url.path_segments(
                base_url.path_segments() + ("meetingPreferences", "personalMeetingRoom")
            ).query_param("userEmail", p.email)
            with client.get(url.as_string()) as resp:
                if task.request.id:
                    task.update_state(
                        state="PROGRESS", meta={"current": i, "total": total}
                    )
                try:
                    resp.raise_for_status()
                except requests.exceptions.RequestException as e:
                    logger.error(
                        f"Failed to fetch personal room information for {p}: {e}"
                    )
                    continue
                j = resp.json()
                obj, created = models.PersonRoom.objects.update_or_create(
                    pk=p.pk,
                    defaults={
                        "modified": timezone.now(),
                        "url": j.get("personalMeetingRoomLink"),
                        "sip": j.get("sipAddress"),
                        "call_in": [
                            phonenumbers.format_number(
                                phonenumbers.parse(n.get("callInNumber")),
                                phonenumbers.PhoneNumberFormat.E164,
                            )
                            for n in j.get("telephony").get("callInNumbers")
                        ],
                    },
                )
                if created:
                    logger.debug(f"Created new person room {obj}")
                else:
                    logger.debug(f"Updated person room {obj}")
        count, _ = models.PersonRoom.objects.filter(
            modified__lte=timezone.now() - timezone.timedelta(hours=1)
        ).delete()
        if count > 0:
            logger.info(f"Deleted {count} outdated person rooms")
