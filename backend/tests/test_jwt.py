import pytest
from ..src.gallery.models.bases import auth_credential
from ..src.gallery.models import sign_up
import datetime as datetime_module


example = sign_up.SignUp(
    expiry=datetime_module.datetime(
        2023, 10, 1, 12, 0, 0, tzinfo=datetime_module.timezone.utc
    ),
    issued=datetime_module.datetime(
        2023, 10, 12, 12, 0, 0, tzinfo=datetime_module.timezone.utc
    ),
    email='a@a.com',
)


def test_from_payload():

    instance = sign_up.SignUp.from_payload(
        {
            'exp': example.expiry.timestamp(),
            'iat': example.issued.timestamp(),
            'sub': example.email,
            'type': example.auth_type,
        }
    )

    assert instance == example


def test_to_payload():

    payload = sign_up.SignUp.to_payload(example)

    assert payload == {
        'exp': example.expiry,
        'iat': example.issued,
        'sub': example.email,
        'type': example.auth_type,
    }
