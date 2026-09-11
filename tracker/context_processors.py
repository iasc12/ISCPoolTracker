from .models import Membership, MpesaPayment


def membership_nav(request):

    context = {
        "pending_membership_count": 0,
        "navbar_membership_status": None,
    }

    if not request.user.is_authenticated:
        return context

    if request.user.is_superuser:

        context["pending_membership_count"] = (
            MpesaPayment.objects
            .filter(
                status=MpesaPayment.STATUS_PENDING,
            )
            .count()
        )

        context["navbar_membership_status"] = "Owner"

        return context

    membership = (
        Membership.objects
        .filter(user=request.user)
        .first()
    )

    if membership:

        if (
            membership.status == Membership.STATUS_TRIAL
            and membership.is_active
        ):
            context["navbar_membership_status"] = "Trial"

        elif (
            membership.status == Membership.STATUS_ACTIVE
            and membership.is_active
        ):
            context["navbar_membership_status"] = "Active"

        else:
            context["navbar_membership_status"] = "Expired"

    return context
