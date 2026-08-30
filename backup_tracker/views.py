from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DailyEarningForm, ExpenseForm
from .models import DailyEarning, Expense


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(request):
    today = date.today()

    # Monday = start of week
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # First and last day of month
    month_start = today.replace(day=1)

    if month_start.month == 12:
        next_month = month_start.replace(
            year=month_start.year + 1,
            month=1,
            day=1,
        )
    else:
        next_month = month_start.replace(
            month=month_start.month + 1,
            day=1,
        )

    month_end = next_month - timedelta(days=1)

    # --------------------------------------------------------
    # TODAY
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # WEEK
    # --------------------------------------------------------

    weekly_earnings = (
        DailyEarning.objects
        .filter(date__range=[week_start, week_end])
        .aggregate(total=Sum("amount_collected"))
        .get("total")
        or Decimal("0.00")
    )

    weekly_expenses = (
        Expense.objects
        .filter(date__range=[week_start, week_end])
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0.00")
    )

    weekly_profit = weekly_earnings - weekly_expenses

    # --------------------------------------------------------
    # MONTH
    # --------------------------------------------------------

    monthly_earnings = (
        DailyEarning.objects
        .filter(date__range=[month_start, month_end])
        .aggregate(total=Sum("amount_collected"))
        .get("total")
        or Decimal("0.00")
    )

    monthly_expenses = (
        Expense.objects
        .filter(date__range=[month_start, month_end])
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0.00")
    )

    monthly_profit = monthly_earnings - monthly_expenses

    # --------------------------------------------------------
    # LAST 7 DAYS CHART
    # --------------------------------------------------------

    chart_labels = []
    chart_values = []

    for i in range(6, -1, -1):
        current_day = today - timedelta(days=i)

        amount = (
            DailyEarning.objects
            .filter(date=current_day)
            .aggregate(total=Sum("amount_collected"))
            .get("total")
            or Decimal("0.00")
        )

        chart_labels.append(
            current_day.strftime("%d %b")
        )

        chart_values.append(float(amount))

    # --------------------------------------------------------
    # RECENT ACTIVITY
    # --------------------------------------------------------

    recent_earnings = (
        DailyEarning.objects
        .order_by("-date", "-created_at")[:5]
    )

    recent_expenses = (
        Expense.objects
        .order_by("-date", "-created_at")[:5]
    )

    context = {
        "today": today,

        "week_start": week_start,
        "week_end": week_end,

        "month_start": month_start,
        "month_end": month_end,

        "today_earnings": today_earnings,
        "today_expenses": today_expenses,
        "today_profit": today_profit,

        "weekly_earnings": weekly_earnings,
        "weekly_expenses": weekly_expenses,
        "weekly_profit": weekly_profit,

        "monthly_earnings": monthly_earnings,
        "monthly_expenses": monthly_expenses,
        "monthly_profit": monthly_profit,

        "chart_labels": chart_labels,
        "chart_values": chart_values,

        "recent_earnings": recent_earnings,
        "recent_expenses": recent_expenses,
    }

    return render(
        request,
        "tracker/dashboard.html",
        context,
    )


# ============================================================
# EARNINGS
# ============================================================

def add_earning(request):
    if request.method == "POST":
        form = DailyEarningForm(request.POST)

        if form.is_valid():
            earning = form.save()

            messages.success(
                request,
                f"Earning of KSh {earning.amount_collected:,.2f} "
                f"saved successfully."
            )

            return redirect("dashboard")

    else:
        form = DailyEarningForm(
            initial={
                "date": date.today(),
            }
        )

    return render(
        request,
        "tracker/add_earning.html",
        {
            "form": form,
        },
    )


def earnings_list(request):
    earnings = DailyEarning.objects.all()

    total = (
        earnings.aggregate(total=Sum("amount_collected"))
        .get("total")
        or Decimal("0.00")
    )

    return render(
        request,
        "tracker/earnings_list.html",
        {
            "earnings": earnings,
            "total": total,
        },
    )


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
            earning = form.save()

            messages.success(
                request,
                f"Earning updated successfully. "
                f"KSh {earning.amount_collected:,.2f}"
            )

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
            "editing": True,
            "earning": earning,
        },
    )


def delete_earning(request, earning_id):
    earning = get_object_or_404(
        DailyEarning,
        id=earning_id,
    )

    if request.method == "POST":
        amount = earning.amount_collected
        earning.delete()

        messages.success(
            request,
            f"Earning of KSh {amount:,.2f} deleted successfully."
        )

        return redirect("earnings_list")

    return render(
        request,
        "tracker/delete_confirm.html",
        {
            "object": earning,
            "object_type": "earning",
            "cancel_url": "earnings_list",
        },
    )


# ============================================================
# EXPENSES
# ============================================================

def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save()

            messages.success(
                request,
                f"Expense of KSh {expense.amount:,.2f} "
                f"saved successfully."
            )

            return redirect("dashboard")

    else:
        form = ExpenseForm(
            initial={
                "date": date.today(),
            }
        )

    return render(
        request,
        "tracker/add_expense.html",
        {
            "form": form,
        },
    )


def expenses_list(request):
    expenses = Expense.objects.all()

    total = (
        expenses.aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0.00")
    )

    return render(
        request,
        "tracker/expenses_list.html",
        {
            "expenses": expenses,
            "total": total,
        },
    )


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
            expense = form.save()

            messages.success(
                request,
                f"Expense updated successfully. "
                f"KSh {expense.amount:,.2f}"
            )

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
            "expense": expense,
        },
    )


def delete_expense(request, expense_id):
    expense = get_object_or_404(
        Expense,
        id=expense_id,
    )

    if request.method == "POST":
        amount = expense.amount
        expense.delete()

        messages.success(
            request,
            f"Expense of KSh {amount:,.2f} deleted successfully."
        )

        return redirect("expenses_list")

    return render(
        request,
        "tracker/delete_confirm.html",
        {
            "object": expense,
            "object_type": "expense",
            "cancel_url": "expenses_list",
        },
    )


# ============================================================
# REPORTS
# ============================================================

def reports(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    earnings = DailyEarning.objects.all()
    expenses = Expense.objects.all()

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    if start_date:
        earnings = earnings.filter(date__gte=start_date)
        expenses = expenses.filter(date__gte=start_date)

    if end_date:
        earnings = earnings.filter(date__lte=end_date)
        expenses = expenses.filter(date__lte=end_date)

    # --------------------------------------------------------
    # TOTALS
    # --------------------------------------------------------

    total_earnings = (
        earnings.aggregate(total=Sum("amount_collected"))
        .get("total")
        or Decimal("0.00")
    )

    total_expenses = (
        expenses.aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0.00")
    )

    total_profit = total_earnings - total_expenses

    # --------------------------------------------------------
    # EARNING DAYS
    # --------------------------------------------------------

    earning_days = (
        earnings.values("date")
        .distinct()
        .count()
    )

    if earning_days > 0:
        average_daily_earnings = (
            total_earnings / Decimal(earning_days)
        )
    else:
        average_daily_earnings = Decimal("0.00")

    # --------------------------------------------------------
    # MONTHLY FORECAST
    # --------------------------------------------------------

    forecast_monthly = (
        average_daily_earnings * Decimal("30")
    )

    # --------------------------------------------------------
    # PROFIT MARGIN
    # --------------------------------------------------------

    if total_earnings > 0:
        profit_margin = (
            total_profit / total_earnings
        ) * Decimal("100")
    else:
        profit_margin = Decimal("0.00")

    # --------------------------------------------------------
    # EXPENSE BREAKDOWN
    # --------------------------------------------------------

    breakdown = (
        expenses
        .values("expense_type")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    expense_breakdown = []

    for item in breakdown:
        amount = item["total"] or Decimal("0.00")

        if total_expenses > 0:
            percentage = (
                amount / total_expenses
            ) * Decimal("100")
        else:
            percentage = Decimal("0.00")

        # Get readable name from model choices
        display_name = dict(
            Expense.EXPENSE_TYPE_CHOICES
        ).get(
            item["expense_type"],
            item["expense_type"],
        )

        expense_breakdown.append(
            {
                "type": display_name,
                "amount": amount,
                "percentage": percentage,
            }
        )

    # --------------------------------------------------------
    # BEST EARNING DAY
    # --------------------------------------------------------

    best_day = (
        earnings
        .order_by("-amount_collected")
        .first()
    )

    # --------------------------------------------------------
    # HIGHEST EXPENSE
    # --------------------------------------------------------

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

        "earning_days": earning_days,
        "average_daily_earnings": average_daily_earnings,
        "forecast_monthly": forecast_monthly,
        "profit_margin": profit_margin,

        "expense_breakdown": expense_breakdown,

        "best_day": best_day,
        "highest_expense": highest_expense,
    }

    return render(
        request,
        "tracker/reports.html",
        context,
    )


# ============================================================
# GENERATE REPORT
# ============================================================

def generate_report(request):
    return redirect("reports")