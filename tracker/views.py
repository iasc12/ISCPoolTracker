from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import DailyEarningForm, ExpenseForm
from .models import DailyEarning, Expense


def dashboard(request):
    today = timezone.localdate()

    # ============================================================
    # TODAY
    # ============================================================

    today_earning = (
        DailyEarning.objects
        .filter(date=today)
        .first()
    )

    today_earnings = (
        DailyEarning.objects
        .filter(date=today)
        .aggregate(
            total=Sum("amount_collected")
        )["total"]
        or Decimal("0.00")
    )

    today_expenses = (
        Expense.objects
        .filter(date=today)
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    today_profit = (
        today_earnings - today_expenses
    )

    # ============================================================
    # THIS WEEK
    # ============================================================

    week_start = (
        today - timedelta(days=today.weekday())
    )

    week_end = (
        week_start + timedelta(days=6)
    )

    weekly_earnings = (
        DailyEarning.objects
        .filter(
            date__gte=week_start,
            date__lte=week_end,
        )
        .aggregate(
            total=Sum("amount_collected")
        )["total"]
        or Decimal("0.00")
    )

    weekly_expenses = (
        Expense.objects
        .filter(
            date__gte=week_start,
            date__lte=week_end,
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    weekly_profit = (
        weekly_earnings - weekly_expenses
    )

    # ============================================================
    # THIS MONTH
    # ============================================================

    month_start = today.replace(day=1)

    if today.month == 12:
        next_month = today.replace(
            year=today.year + 1,
            month=1,
            day=1,
        )
    else:
        next_month = today.replace(
            month=today.month + 1,
            day=1,
        )

    month_end = (
        next_month - timedelta(days=1)
    )

    monthly_earnings = (
        DailyEarning.objects
        .filter(
            date__gte=month_start,
            date__lte=month_end,
        )
        .aggregate(
            total=Sum("amount_collected")
        )["total"]
        or Decimal("0.00")
    )

    monthly_expenses = (
        Expense.objects
        .filter(
            date__gte=month_start,
            date__lte=month_end,
        )
        .aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    monthly_profit = (
        monthly_earnings - monthly_expenses
    )

    # ============================================================
    # EXPECTED MONTHLY EARNINGS
    #
    # Uses only the days that have earnings recorded
    # during the current month.
    # ============================================================

    month_earning_days = (
        DailyEarning.objects
        .filter(
            date__gte=month_start,
            date__lte=today,
        )
        .count()
    )

    if month_earning_days > 0:
        average_daily_earnings = (
            monthly_earnings
            / Decimal(month_earning_days)
        )

        expected_monthly_earnings = (
            average_daily_earnings
            * Decimal(month_end.day)
        )
    else:
        average_daily_earnings = Decimal("0.00")
        expected_monthly_earnings = Decimal("0.00")

    # ============================================================
    # RECENT EARNINGS
    # ============================================================

    recent_earnings = (
        DailyEarning.objects
        .order_by("-date", "-created_at")[:5]
    )

    # ============================================================
    # RECENT EXPENSES
    # ============================================================

    recent_expenses = (
        Expense.objects
        .order_by("-date", "-created_at")[:5]
    )

    # ============================================================
    # CONTEXT
    # ============================================================

    context = {
        "today": today,

        # Today
        "today_earning": today_earning,
        "today_earnings": today_earnings,
        "today_expenses": today_expenses,
        "today_profit": today_profit,

        # Week
        "week_start": week_start,
        "week_end": week_end,
        "weekly_earnings": weekly_earnings,
        "weekly_expenses": weekly_expenses,
        "weekly_profit": weekly_profit,

        # Month
        "month_start": month_start,
        "month_end": month_end,
        "monthly_earnings": monthly_earnings,
        "monthly_expenses": monthly_expenses,
        "monthly_profit": monthly_profit,

        # Expected month
        "average_daily_earnings": average_daily_earnings,
        "expected_monthly_earnings": expected_monthly_earnings,

        # Recent activity
        "recent_earnings": recent_earnings,
        "recent_expenses": recent_expenses,
    }

    return render(
        request,
        "tracker/dashboard.html",
        context,
    )


# ================================================================
# ADD / EDIT TODAY'S EARNING
# ================================================================

def add_earning(request):
    today = timezone.localdate()

    today_earning = (
        DailyEarning.objects
        .filter(date=today)
        .first()
    )

    if request.method == "POST":

        form = DailyEarningForm(
            request.POST,
            instance=today_earning,
        )

        if form.is_valid():

            earning = form.save(
                commit=False
            )

            # Never allow the user to choose
            # another date here.
            earning.date = today

            earning.save()

            return redirect("dashboard")

    else:

        form = DailyEarningForm(
            instance=today_earning
        )

    return render(
        request,
        "tracker/add_earning.html",
        {
            "form": form,
            "today": today,
            "editing": today_earning is not None,
        },
    )


# ================================================================
# ADD EXPENSE
# ================================================================

def add_expense(request):

    if request.method == "POST":

        form = ExpenseForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect("dashboard")

    else:

        form = ExpenseForm()

    return render(
        request,
        "tracker/add_expense.html",
        {
            "form": form,
        },
    )