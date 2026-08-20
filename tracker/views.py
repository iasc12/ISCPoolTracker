from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import redirect, render

from .forms import DailyEarningForm, ExpenseForm
from .models import DailyEarning, Expense


def dashboard(request):
    earnings = DailyEarning.objects.all()
    expenses = Expense.objects.all()

    # -----------------------------
    # TOTALS
    # -----------------------------

    total_earnings = (
        earnings.aggregate(
            total=Sum("amount_collected")
        )["total"]
        or Decimal("0.00")
    )

    total_expenses = (
        expenses.aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    net_profit = (
        total_earnings - total_expenses
    )

    # -----------------------------
    # RECENT 7 DAYS
    # -----------------------------

    recent_earnings = earnings[:7]

    chart_labels = [
        earning.date.strftime("%d %b")
        for earning in reversed(recent_earnings)
    ]

    chart_values = [
        float(earning.amount_collected)
        for earning in reversed(recent_earnings)
    ]

    # -----------------------------
    # AVERAGE DAILY EARNINGS
    # -----------------------------

    earning_count = earnings.count()

    if earning_count:
        average_daily_earnings = (
            total_earnings / earning_count
        )
    else:
        average_daily_earnings = Decimal("0.00")

    # -----------------------------
    # HIGHEST EARNING DAY
    # -----------------------------

    highest_earning = (
        earnings.order_by(
            "-amount_collected"
        ).first()
    )

    # -----------------------------
    # RECENT RECORDS
    # -----------------------------

    recent_records = earnings[:10]
    recent_expenses = expenses[:10]

    context = {
        "total_earnings": total_earnings,
        "total_expenses": total_expenses,
        "net_profit": net_profit,

        "average_daily_earnings": (
            average_daily_earnings
        ),

        "highest_earning": highest_earning,

        "recent_records": recent_records,
        "recent_expenses": recent_expenses,

        "chart_labels": chart_labels,
        "chart_values": chart_values,
    }

    return render(
        request,
        "tracker/dashboard.html",
        context,
    )


def add_earning(request):

    if request.method == "POST":

        form = DailyEarningForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "dashboard"
            )

    else:

        form = DailyEarningForm()

    return render(
        request,
        "tracker/add_earning.html",
        {
            "form": form,
        },
    )


def add_expense(request):

    if request.method == "POST":

        form = ExpenseForm(
            request.POST
        )

        if form.is_valid():

            form.save()

            return redirect(
                "dashboard"
            )

    else:

        form = ExpenseForm()

    return render(
        request,
        "tracker/add_expense.html",
        {
            "form": form,
        },
    )