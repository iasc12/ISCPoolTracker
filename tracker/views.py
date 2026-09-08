from django.core.paginator import Paginator
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DailyEarningForm, ExpenseForm
from .models import DailyEarning, Expense


def money(value):
    if value is None:
        return Decimal("0.00")
    return Decimal(value)


def dashboard(request):

    today = date.today()

    # ---------------------------------------------------------
    # DATE RANGES
    # ---------------------------------------------------------

    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    month_start = today.replace(day=1)

    if month_start.month == 12:
        next_month = date(month_start.year + 1, 1, 1)
    else:
        next_month = date(
            month_start.year,
            month_start.month + 1,
            1
        )

    month_end = next_month - timedelta(days=1)

    # ---------------------------------------------------------
    # TODAY
    # ---------------------------------------------------------

    today_earnings = money(
        DailyEarning.objects.filter(
            date=today
        ).aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    today_expenses = money(
        Expense.objects.filter(
            date=today
        ).aggregate(
            total=Sum("amount")
        )["total"]
    )

    today_profit = today_earnings - today_expenses

    # ---------------------------------------------------------
    # WEEK
    # ---------------------------------------------------------

    weekly_earnings = money(
        DailyEarning.objects.filter(
            date__range=[week_start, week_end]
        ).aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    weekly_expenses = money(
        Expense.objects.filter(
            date__range=[week_start, week_end]
        ).aggregate(
            total=Sum("amount")
        )["total"]
    )

    weekly_profit = weekly_earnings - weekly_expenses

    # ---------------------------------------------------------
    # MONTH
    # ---------------------------------------------------------

    monthly_earnings = money(
        DailyEarning.objects.filter(
            date__range=[month_start, month_end]
        ).aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    monthly_expenses = money(
        Expense.objects.filter(
            date__range=[month_start, month_end]
        ).aggregate(
            total=Sum("amount")
        )["total"]
    )

    monthly_profit = monthly_earnings - monthly_expenses

    # ---------------------------------------------------------
    # PROFIT MARGINS
    # ---------------------------------------------------------

    if today_earnings:
        today_profit_margin = (
            today_profit / today_earnings
        ) * Decimal("100")
    else:
        today_profit_margin = Decimal("0.00")

    if weekly_earnings:
        weekly_profit_margin = (
            weekly_profit / weekly_earnings
        ) * Decimal("100")
    else:
        weekly_profit_margin = Decimal("0.00")

    if monthly_earnings:
        monthly_profit_margin = (
            monthly_profit / monthly_earnings
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
        DailyEarning.objects.aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    total_expenses = money(
        Expense.objects.aggregate(
            total=Sum("amount")
        )["total"]
    )

    total_profit = total_earnings - total_expenses

    if earning_days > 0:

        average_daily_earnings = (
            total_earnings / Decimal(earning_days)
        )

        average_daily_profit = (
            total_profit / Decimal(earning_days)
        )

    else:

        average_daily_earnings = Decimal("0.00")
        average_daily_profit = Decimal("0.00")

    # ---------------------------------------------------------
    # EXPECTED EARNINGS
    # ---------------------------------------------------------

    expected_weekly_earnings = (
        average_daily_earnings * Decimal("7")
    )

    expected_monthly_earnings = (
        average_daily_earnings * Decimal("30")
    )

    # ---------------------------------------------------------
    # BEST AND LOWEST EARNING DAYS
    # ---------------------------------------------------------

    best_day = (
        DailyEarning.objects
        .order_by("-amount_collected", "-date")
        .first()
    )

    lowest_day = (
        DailyEarning.objects
        .order_by("amount_collected", "date")
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

        chart_date = today - timedelta(days=i)

        daily_earnings = money(
            DailyEarning.objects.filter(
                date=chart_date
            ).aggregate(
                total=Sum("amount_collected")
            )["total"]
        )

        daily_expenses = money(
            Expense.objects.filter(
                date=chart_date
            ).aggregate(
                total=Sum("amount")
            )["total"]
        )

        daily_profit = (
            daily_earnings - daily_expenses
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

    target_monthly = Decimal("50000.00")

    target_progress = Decimal("0.00")

    if target_monthly > 0:
        target_progress = (
            monthly_earnings / target_monthly
        ) * Decimal("100")

    if target_progress > Decimal("100"):
        target_progress = Decimal("100")

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
        "expected_weekly_earnings": expected_weekly_earnings,
        "expected_monthly_earnings": expected_monthly_earnings,

        # Best / lowest
        "best_day": best_day,
        "lowest_day": lowest_day,

        # Charts
        "chart_labels": chart_labels,
        "chart_values": earnings_chart_values,
        "earnings_chart_values": earnings_chart_values,
        "expense_chart_values": expense_chart_values,
        "profit_chart_values": profit_chart_values,

        # Target
        "target_monthly": target_monthly,
        "target_progress": target_progress,

        # Recent
        "recent_earnings": DailyEarning.objects.all().order_by(
            "-date", "-id"
        )[:5],

        "recent_expenses": Expense.objects.all().order_by(
            "-date", "-id"
        )[:5],
    }

    return render(
        request,
        "tracker/dashboard.html",
        context
    )

def add_earning(request):

    if request.method == "POST":
        form = DailyEarningForm(request.POST)

        if form.is_valid():
            earning = form.save()

            messages.success(
                request,
                f"Earning of KSh {earning.amount_collected:.2f} saved successfully."
            )

            return redirect("dashboard")

    else:
        form = DailyEarningForm(
            initial={"date": date.today()}
        )

    return render(
        request,
        "tracker/add_earning.html",
        {"form": form}
    )


def earnings_list(request):

    earnings = DailyEarning.objects.all().order_by("-date", "-id")

    total = money(
        earnings.aggregate(
            total=Sum("amount_collected")
        )["total"]
    )

    paginator = Paginator(earnings, 7)
    page_number = request.GET.get("page")
    earnings_page = paginator.get_page(page_number)

    return render(
        request,
        "tracker/earnings_list.html",
        {
            "earnings": earnings_page,
            "total": total,
        }
    )

def edit_earning(request, earning_id):

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
                f"Earning of KSh {earning.amount_collected:.2f} updated successfully."
            )

            return redirect("earnings_list")

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


def delete_earning(request, earning_id):

    earning = get_object_or_404(
        DailyEarning,
        id=earning_id
    )

    if request.method == "POST":
        amount = earning.amount_collected
        earning.delete()

        messages.success(
            request,
            f"Earning of KSh {amount:.2f} deleted successfully."
        )

        return redirect("earnings_list")

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
        form = ExpenseForm(request.POST)

        if form.is_valid():
            expense = form.save()

            messages.success(
                request,
                f"Expense of KSh {expense.amount:.2f} saved successfully."
            )

            return redirect("dashboard")

    else:
        form = ExpenseForm(
            initial={"date": date.today()}
        )

    return render(
        request,
        "tracker/add_expense.html",
        {"form": form}
    )


def expenses_list(request):

    expenses = Expense.objects.all().order_by("-date", "-id")

    total = money(
        expenses.aggregate(
            total=Sum("amount")
        )["total"]
    )

    paginator = Paginator(expenses, 7)
    page_number = request.GET.get("page")
    expenses_page = paginator.get_page(page_number)

    return render(
        request,
        "tracker/expenses_list.html",
        {
            "expenses": expenses_page,
            "total": total,
        }
    )

def edit_expense(request, expense_id):

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
                f"Expense of KSh {expense.amount:.2f} updated successfully."
            )

            return redirect("expenses_list")

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


def delete_expense(request, expense_id):

    expense = get_object_or_404(
        Expense,
        id=expense_id
    )

    if request.method == "POST":
        amount = expense.amount
        expense.delete()

        messages.success(
            request,
            f"Expense of KSh {amount:.2f} deleted successfully."
        )

        return redirect("expenses_list")

    return render(
        request,
        "tracker/delete_confirm.html",
        {
            "object": expense,
            "object_type": "expense",
        }
    )


def reports(request):

    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    earnings = DailyEarning.objects.all()
    expenses = Expense.objects.all()

    if start_date:
        earnings = earnings.filter(date__gte=start_date)
        expenses = expenses.filter(date__gte=start_date)

    if end_date:
        earnings = earnings.filter(date__lte=end_date)
        expenses = expenses.filter(date__lte=end_date)

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

    total_profit = total_earnings - total_expenses

    earning_dates = earnings.values("date").distinct().count()

    if earning_dates:
        average_daily_earnings = (
            total_earnings / Decimal(earning_dates)
        )
    else:
        average_daily_earnings = Decimal("0.00")

    if total_earnings:
        profit_margin = (
            total_profit / total_earnings
        ) * Decimal("100")
    else:
        profit_margin = Decimal("0.00")

    forecast_monthly = (
        average_daily_earnings * Decimal("30")
    )

    breakdown = []

    expense_types = expenses.values(
        "expense_type"
    ).distinct()

    for row in expense_types:

        expense_type = row["expense_type"]

        amount = money(
            expenses.filter(
                expense_type=expense_type
            ).aggregate(
                total=Sum("amount")
            )["total"]
        )

        if total_expenses:
            percentage = (
                amount / total_expenses
            ) * Decimal("100")
        else:
            percentage = Decimal("0.00")

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
        .order_by("-amount_collected")
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
        "average_daily_earnings": average_daily_earnings,
        "forecast_monthly": forecast_monthly,
        "profit_margin": profit_margin,

        "expense_breakdown": breakdown,

        "best_day": best_day,
        "highest_expense": highest_expense,
    }

    return render(
        request,
        "tracker/reports.html",
        context
    )


def generate_report(request):

    return redirect("reports")





