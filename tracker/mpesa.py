import base64
from datetime import datetime

import requests

from django.conf import settings
from django.utils import timezone


def _get_mpesa_base_url():
    """
    Return the correct Daraja API base URL.
    """

    environment = (
        getattr(settings, "MPESA_ENVIRONMENT", "sandbox")
        or "sandbox"
    ).strip().lower()

    if environment == "production":
        return "https://api.safaricom.co.ke"

    return "https://sandbox.safaricom.co.ke"


def _validate_mpesa_settings():
    """
    Make sure the credentials/configuration required by Daraja exist.
    """

    required_settings = {
        "MPESA_CONSUMER_KEY": settings.MPESA_CONSUMER_KEY,
        "MPESA_CONSUMER_SECRET": settings.MPESA_CONSUMER_SECRET,
        "MPESA_SHORTCODE": settings.MPESA_SHORTCODE,
        "MPESA_PASSKEY": settings.MPESA_PASSKEY,
        "MPESA_CALLBACK_URL": settings.MPESA_CALLBACK_URL,
    }

    missing = [
        name
        for name, value in required_settings.items()
        if not str(value).strip()
    ]

    if missing:
        raise RuntimeError(
            "Missing M-Pesa configuration: "
            + ", ".join(missing)
        )


def get_mpesa_access_token():
    """
    Get an OAuth access token from Safaricom Daraja.
    """

    _validate_mpesa_settings()

    base_url = _get_mpesa_base_url()

    url = (
        f"{base_url}/oauth/v1/generate"
        "?grant_type=client_credentials"
    )

    response = requests.get(
        url,
        auth=(
            settings.MPESA_CONSUMER_KEY,
            settings.MPESA_CONSUMER_SECRET,
        ),
        timeout=30,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"M-Pesa OAuth request failed "
            f"({response.status_code}): "
            f"{response.text[:500]}"
        ) from exc

    data = response.json()

    access_token = data.get("access_token")

    if not access_token:
        raise RuntimeError(
            "M-Pesa OAuth response did not contain an access token."
        )

    return access_token


def generate_password(timestamp):
    """
    Generate the Daraja STK Push password.

    Password =
        Base64(
            BusinessShortCode + Passkey + Timestamp
        )
    """

    raw = (
        f"{settings.MPESA_SHORTCODE}"
        f"{settings.MPESA_PASSKEY}"
        f"{timestamp}"
    )

    return base64.b64encode(
        raw.encode("utf-8")
    ).decode("utf-8")


def _generate_timestamp():
    """
    Generate the Daraja timestamp in YYYYMMDDHHMMSS format.

    Django's timezone.now() is used so the project does not depend
    on the operating system's naive local datetime configuration.
    """

    current_time = timezone.localtime(timezone.now())

    return current_time.strftime("%Y%m%d%H%M%S")


def initiate_stk_push(phone_number, amount, account_reference):
    """
    Send an STK Push request to the customer's phone.
    """

    _validate_mpesa_settings()

    access_token = get_mpesa_access_token()

    timestamp = _generate_timestamp()

    password = generate_password(timestamp)

    base_url = _get_mpesa_base_url()

    url = (
        f"{base_url}"
        "/mpesa/stkpush/v1/processrequest"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "BusinessShortCode": str(settings.MPESA_SHORTCODE),
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": str(phone_number),
        "PartyB": str(settings.MPESA_SHORTCODE),
        "PhoneNumber": str(phone_number),
        "CallBackURL": str(settings.MPESA_CALLBACK_URL),
        "AccountReference": str(account_reference)[:12],
        "TransactionDesc": "ISC Pool Tracker Membership",
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=30,
    )

    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise RuntimeError(
            f"M-Pesa STK Push request failed "
            f"({response.status_code}): "
            f"{response.text[:500]}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            "M-Pesa returned an invalid JSON response."
        ) from exc

    return data
