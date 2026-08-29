from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DailyEarningForm, ExpenseForm
from .models import DailyEarning, Expense


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(request):
    today = timezone.localdate()

    period = request.GET.get("period", "month")

    if period == "today":
        start_date = today
        end_date = today
        period_label = "Today"

    elif period == "week":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        period_label = "This Week"

    elif period == "last_month":
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)

        start_date = last_month_end.replace(day=1)
        end_date = last_month_end
        period_label = "Last Month"

    elif period == "custom":
        start_string = request.GET.get("start_date")
        end_string = request.GET.get("end_date")

        try:
            start_date = timezone.datetime.strptime(
                start_string,
                "%Y-%m-%d",
            ).date()

            end_date = timezone.datetime.strptime(
                end_string,
                "%Y-%m-%d",
            ).date()

            if start_date > end_date:
                start_date, end_date = end_date, start_date

            period_label = (
                f"{start_date.strftime('%d %b %Y')} – "
                f"{end_date.strftime('%d %b %Y')}"
            )

        except (TypeError, ValueError):
            period = "month"
            start_date = today.replace(day=1)

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

            end_date = next_month - timedelta(days=1)
            period_label = "This Month"

    else:
        period = "month"
        start_date = today.replace(day=1)

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

        end_date = next_month - timedelta(days=1)
        period_label = "This Month"

    # ========================================================
    # FILTERED DATA
    # ========================================================

    filtered_earnings = DailyEarning.objects.filter(
        date__range=(start_date, end_date)
    )

    filtered_expenses = Expense.objects.filter(
        date__range=(start_date, end_date)
    )

    # ========================================================
    # PERIOD TOTALS
    # ========================================================

    period_earnings = (
        filtered_earnings.aggregate(
            total=Sum("amount_collected")
        ).get("total")
        or Decimal("0.00")
    )

    period_expenses = (
        filtered_expenses.aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0.00")
    )

    period_profit = period_earnings - period_expenses

    # ========================================================
    # TODAY
    # ========================================================

    today_earnings = (
        DailyEarning.objects.filter(
            date=today
        ).aggregate(
            total=Sum("amount_collected")
        ).get("total")
        or Decimal("0.00")
    )

    today_expenses = (
        Expense.objects.filter(
            date=today
        ).aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0.00")
    )

    today_profit = today_earnings - today_expenses

    # ========================================================
    # WEEK
    # ========================================================

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    weekly_earnings = (
        DailyEarning.objects.filter(
            date__range=(week_start, week_end)
        ).aggregate(
            total=Sum("amount_collected")
        ).get("total")
        or Decimal("0.00")
    )

    weekly_expenses = (
        Expense.objects.filter(
            date__range=(week_start, week_end)
        ).aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0.00")
    )

    weekly_profit = weekly_earnings - weekly_expenses

    # ========================================================
    # MONTH
    # ========================================================

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
        DailyEarning.objects.filter(
            date__range=(month_start, month_end)
        ).aggregate(
            total=Sum("amount_collected")
        ).get("total")
        or Decimal("0.00")
    )

    monthly_expenses = (
        Expense.objects.filter(
            date__range=(month_start, month_end)
        ).aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0.00")
    )

    monthly_profit = monthly_earnings - monthly_expenses

    # ========================================================
    # AVERAGE / FORECAST
    # ========================================================

    earning_days = filtered_earnings.count()

    if earning_days:
        average_daily_earnings = (
            period_earnings / Decimal(earning_days)
        )
    else:
        average_daily_earnings = Decimal("0.00")

    forecast_monthly = (
        average_daily_earnings * Decimal("30")
    )

    if period_earnings > 0:
        profit_margin = (
            period_profit / period_earnings
        ) * Decimal("100")
    else:
        profit_margin = Decimal("0.00")

    # ========================================================
    # RECENT ACTIVITY
    # ========================================================

    recent_earnings = DailyEarning.objects.order_by(
        "-date",
        "-created_at",
    )[:5]

    recent_expenses = Expense.objects.order_by(
        "-date",
        "-created_at",
    )[:5]

    # ========================================================
    # CHART
    # ========================================================

    chart_labels = []
    chart_values = []

    chart_start = max(
        start_date,
        end_date - timedelta(days=6),
    )

    current_date = chart_start

    while current_date <= end_date:

        earning = (
            DailyEarning.objects.filter(
                date=current_date
            ).first()
        )

        chart_labels.append(
            current_date.strftime("%d %b")
        )

        if earning:
            chart_values.append(
                float(earning.amount_collected)
            )
        else:
            chart_values.append(0)

        current_date += timedelta(days=1)

    # ========================================================
    # EXPENSE BREAKDOWN
    # ========================================================

    expense_breakdown = []

    for value, label in Expense.EXPENSE_TYPE_CHOICES:

        amount = (
            filtered_expenses.filter(
                expense_type=value
            ).aggregate(
                total=Sum("amount")
            ).get("total")
            or Decimal("0.00")
        )

        expense_breakdown.append({
            "type": label,
            "amount": amount,
        })

    # ========================================================
    # CONTEXT
    # ========================================================

    context = {
        "period": period,
        "period_label": period_label,
        "start_date": start_date,
        "end_date": end_date,

        "period_earnings": period_earnings,
        "period_expenses": period_expenses,
        "period_profit": period_profit,

        "average_daily_earnings": average_daily_earnings,
        "forecast_monthly": forecast_monthly,
        "expected_monthly_earnings": forecast_monthly,
        "profit_margin": profit_margin,

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

        "recent_earnings": recent_earnings,
        "recent_expenses": recent_expenses,

        "chart_labels": chart_labels,
        "chart_values": chart_values,

        "expense_breakdown": expense_breakdown,
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

    if request.method == "POST":
        form = DailyEarningForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Earning added successfully."
            )

            return redirect("earnings_list")

    else:
        form = DailyEarningForm()

    return render(
        request,
        "tracker/earning_form.html",
        {
            "form": form,
            "title": "Add Earning",
        },
    )


# ============================================================
# EARNINGS LIST
# ============================================================

def earnings_list(request):

    earnings = DailyEarning.objects.order_by(
        "-date",
        "-created_at",
    )

    total = (
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
            "total": total,
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

            messages.success(
                request,
                "Earning updated successfully."
            )

            return redirect("earnings_list")

    else:

        form = DailyEarningForm(
            instance=earning
        )

    return render(
        request,
        "tracker/earning_form.html",
        {
            "form": form,
            "title": "Edit Earning",
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

        messages.success(
            request,
            "Earning deleted successfully."
        )

        return redirect("earnings_list")

    return render(
        request,
        "tracker/confirm_delete.html",
        {
            "object": earning,
            "type": "earning",
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

            messages.success(
                request,
                "Expense added successfully."
            )

            return redirect("expenses_list")

    else:
        form = ExpenseForm()

    return render(
        request,
        "tracker/expense_form.html",
        {
            "form": form,
            "title": "Add Expense",
        },
    )


# ============================================================
# EXPENSES LIST
# ============================================================

def expenses_list(request):

    expenses = Expense.objects.order_by(
        "-date",
        "-created_at",
    )

    total = (
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
            "total": total,
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

            messages.success(
                request,
                "Expense updated successfully."
            )

            return redirect("expenses_list")

    else:

        form = ExpenseForm(
            instance=expense
        )

    return render(
        request,
        "tracker/expense_form.html",
        {
            "form": form,
            "title": "Edit Expense",
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

        messages.success(
            request,
            "Expense deleted successfully."
        )

        return redirect("expenses_list")

    return render(
        request,
        "tracker/confirm_delete.html",
        {
            "object": expense,
            "type": "expense",
        },
    )


# ============================================================
# REPORTS
# ============================================================

def reports(request):

    earnings_total = (
        DailyEarning.objects.aggregate(
            total=Sum("amount_collected")
        ).get("total")
        or Decimal("0.00")
    )

    expenses_total = (
        Expense.objects.aggregate(
            total=Sum("amount")
        ).get("total")
        or Decimal("0.00")
    )

    profit = earnings_total - expenses_total

    return render(
        request,
        "tracker/reports.html",
        {
            "earnings_total": earnings_total,
            "expenses_total": expenses_total,
            "profit": profit,
        },
    )