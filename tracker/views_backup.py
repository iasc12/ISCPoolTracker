
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DailyEarningForm, ExpenseForm
from .models import DailyEarning, Expense


def dashboard(request):
    today = timezone.localdate()

    # ==============================
    # TODAY
    # ==============================

    today_earnings = (
        DailyEarning.objects
        .filter(date=today)
        .aggregate(total=Sum("amount_collected"))
        .get("total")
        or Decimal("0.00")
    )

    today_expenses = (
        Expense.objects
        .filter(date=today)
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0.00")
    )

    today_profit = today_earnings - today_expenses

    # ==============================
    # THIS WEEK
    # ==============================

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    weekly_earnings = (
        DailyEarning.objects
        .filter(date__range=(week_start, week_end))
        .aggregate(total=Sum("amount_collected"))
        .get("total")
        or Decimal("0.00")
    )

    weekly_expenses = (
        Expense.objects
        .filter(date__range=(week_start, week_end))
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0.00")
    )

    weekly_profit = weekly_earnings - weekly_expenses

    # ==============================
    # THIS MONTH
    # ==============================

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

    month_end = next_month - timedelta(days=1)

    monthly_earnings = (
        DailyEarning.objects
        .filter(date__range=(month_start, month_end))
        .aggregate(total=Sum("amount_collected"))
        .get("total")
        or Decimal("0.00")
    )

    monthly_expenses = (
        Expense.objects
        .filter(date__range=(month_start, month_end))
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0.00")
    )

    monthly_profit = monthly_earnings - monthly_expenses

    # ==============================
    # AVERAGE & FORECAST
    # ==============================

    earning_days = DailyEarning.objects.count()

    if earning_days:
        total_earnings = (
            DailyEarning.objects
            .aggregate(total=Sum("amount_collected"))
            .get("total")
            or Decimal("0.00")
        )

        average_daily_earnings = (
            total_earnings / Decimal(earning_days)
        )

        expected_monthly_earnings = (
            average_daily_earnings * Decimal(month_end.day)
        )

    else:
        average_daily_earnings = Decimal("0.00")
        expected_monthly_earnings = Decimal("0.00")

    # ==============================
    # RECENT ACTIVITY
    # ==============================

    recent_earnings = (
        DailyEarning.objects
        .order_by("-date", "-created_at")[:5]
    )

    recent_expenses = (
        Expense.objects
        .order_by("-date", "-created_at")[:5]
    )

    # ==============================
    # 7-DAY GRAPH
    # ==============================

    chart_labels = []
    chart_values = []

    for offset in range(6, -1, -1):
        chart_date = today - timedelta(days=offset)

        earning = (
            DailyEarning.objects
            .filter(date=chart_date)
            .first()
        )

        chart_labels.append(
            chart_date.strftime("%d %b")
        )

        if earning:
            chart_values.append(
                float(earning.amount_collected)
            )
        else:
            chart_values.append(0)

    context = {
        "today": today,

        "today_earnings": today_earnings,
        "today_expenses": today_expenses,
        "today_profit": today_profit,

        "week_start": week_start,
        "week_end": week_end,
        "weekly_earnings": weekly_earnings,
        "weekly_expenses": weekly_expenses,
        "weekly_profit": weekly_profit,

        "month_start": month_start,
        "month_end": month_end,
        "monthly_earnings": monthly_earnings,
        "monthly_expenses": monthly_expenses,
        "monthly_profit": monthly_profit,

        "average_daily_earnings": average_daily_earnings,
        "expected_monthly_earnings": expected_monthly_earnings,

        "recent_earnings": recent_earnings,
        "recent_expenses": recent_expenses,

        "chart_labels": chart_labels,
        "chart_values": chart_values,
    }

    return render(
        request,
        "tracker/dashboard.html",
        context,
    )


# ============================================================
# ADD EARNING
# ============================================================

def add_earning(request):
    today = timezone.localdate()

    today_earning = (
        DailyEarning.objects
        .filter(date=today)
        .first()
    )

    if request.method == "POST":

        if today_earning:
            form = DailyEarningForm(
                request.POST,
                instance=today_earning,
            )
        else:
            form = DailyEarningForm(request.POST)

        if form.is_valid():

            earning = form.save(commit=False)
            earning.date = today
            earning.save()

            return redirect("dashboard")

    else:

        if today_earning:
            form = DailyEarningForm(
                instance=today_earning,
            )
        else:
            form = DailyEarningForm()

    return render(
        request,
        "tracker/add_earning.html",
        {
            "form": form,
            "today": today,
            "editing": today_earning is not None,
        },
    )


# ============================================================
# EARNINGS LIST
# ============================================================

def earnings_list(request):

    earnings = (
        DailyEarning.objects
        .order_by("-date", "-created_at")
    )

    total_earnings = (
        earnings.aggregate(
            total=Sum("amount_collected")
        ).get("total")
        or Decimal("0.00")
    )

    return render(
        request,
        "tracker/earnings_list.html",
        {
            "earnings": earnings,
            "total_earnings": total_earnings,
        },
    )


# ============================================================
# EDIT EARNING
# ============================================================

def edit_earning(request, earning_id):

    earning = get_object_or_404(
        DailyEarning,
        id=earning_id,
    )

    if request.method == "POST":

        form = DailyEarningForm(
            request.POST,
            instance=earning,
        )

        if form.is_valid():
            form.save()
            return redirect("earnings_list")

    else:

        form = DailyEarningForm(
            instance=earning,
        )

    return render(
        request,
        "tracker/add_earning.html",
        {
            "form": form,
            "today": earning.date,
            "editing": True,
        },
    )


# ============================================================
# DELETE EARNING
# ============================================================

def delete_earning(request, earning_id):

    earning = get_object_or_404(
        DailyEarning,
        id=earning_id,
    )

    if request.method == "POST":
        earning.delete()
        return redirect("earnings_list")

    return render(
        request,
        "tracker/delete_earning.html",
        {
            "earning": earning,
        },
    )


# ============================================================
# ADD EXPENSE
# ============================================================

def add_expense(request):

    if request.method == "POST":

        form = ExpenseForm(request.POST)

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


# ============================================================
# EXPENSES LIST
# ============================================================

def expenses_list(request):

    expenses = (
        Expense.objects
        .order_by("-date", "-created_at")
    )

    total_expenses = (
        expenses.aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0.00")
    )

    return render(
        request,
        "tracker/expenses_list.html",
        {
            "expenses": expenses,
            "total_expenses": total_expenses,
        },
    )


# ============================================================
# EDIT EXPENSE
# ============================================================

def edit_expense(request, expense_id):

    expense = get_object_or_404(
        Expense,
        id=expense_id,
    )

    if request.method == "POST":

        form = ExpenseForm(
            request.POST,
            instance=expense,
        )

        if form.is_valid():
            form.save()
            return redirect("expenses_list")

    else:

        form = ExpenseForm(
            instance=expense,
        )

    return render(
        request,
        "tracker/add_expense.html",
        {
            "form": form,
            "editing": True,
        },
    )


# ============================================================
# DELETE EXPENSE
# ============================================================

def delete_expense(request, expense_id):

    expense = get_object_or_404(
        Expense,
        id=expense_id,
    )

    if request.method == "POST":
        expense.delete()
        return redirect("expenses_list")

    return render(
        request,
        "tracker/delete_expense.html",
        {
            "expense": expense,
        },
    )