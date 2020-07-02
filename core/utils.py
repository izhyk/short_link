import os
import base64
from django.db import IntegrityError

from core.models import Link
from service.settings import HOST
PREFIX = 'Bearer '


def get_token(header):
    token = header
    if header.startswith(PREFIX):
        token = header[len(PREFIX):]

    return token


def save_encoded_link(user_link, user):
    url_encoded_bytes = base64.b32encode(os.urandom(6))[:6].lower()
    generated_link = str(url_encoded_bytes, "utf-8")
    try:
        Link.objects.create(short_link=generated_link, long_link=user_link, owner=user)
    except IntegrityError:
        return save_encoded_link(user_link, user)

    return HOST + generated_link + '/'
