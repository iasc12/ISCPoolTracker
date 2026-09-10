from datetime import timedelta
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import Membership


def membership_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect_to_login(
                request.get_full_path(),
                reverse("login"),
            )

        # System owner / superuser has permanent access.
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        membership, created = Membership.objects.get_or_create(
            user=request.user,
            defaults={
                "status": Membership.STATUS_TRIAL,
                "trial_started_at": timezone.now(),
                "trial_ends_at": timezone.now() + timedelta(days=7),
            },
        )

        if not membership.is_active:
            return redirect("membership")

        return view_func(request, *args, **kwargs)

    return wrapper
