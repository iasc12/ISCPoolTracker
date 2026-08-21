from datetime import timedelta
from decimal import Decimal, ROUND_CEILING

from django.db.models import Sum
from django.shortcuts import redirect, render
from django.utils import timezone

from .forms import DailyEarningForm, ExpenseForm
from .models import DailyEarning, Expense


def dashboard(request):

    today = timezone.localdate()

    # =================================================
    # ALL-TIME TOTALS
    # =================================================

    total_earnings = (
        DailyEarning.objects.aggregate(
            total=Sum("amount_collected")
        )["total"]
        or Decimal("0.00")
    )

    total_expenses = (
        Expense.objects.aggregate(
            total=Sum("amount")
        )["total"]
        or Decimal("0.00")
    )

    total_profit = (
        total_earnings - total_expenses
    )

    # =================================================
    # TODAY
    # =================================================

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

    # =================================================
    # WEEK
    # =================================================

    week_start = (
        today -
        timedelta(days=today.weekday())
    )

    week_end = (
        week_start +
        timedelta(days=6)
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

    # =================================================
    # MONTH
    # =================================================

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
        next_month -
        timedelta(days=1)
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

    # =================================================
    # LIFETIME DAILY AVERAGE
    # =================================================

    earning_count = (
        DailyEarning.objects.count()
    )

    if earning_count:

        average_daily_earnings = (
            total_earnings /
            Decimal(earning_count)
        )

    else:

        average_daily_earnings = (
            Decimal("0.00")
        )

    # =================================================
    # RECENT 7-DAY AVERAGE
    # =================================================

    seven_days_ago = (
        today - timedelta(days=6)
    )

    recent_7_day_records = (
        DailyEarning.objects
        .filter(
            date__gte=seven_days_ago,
            date__lte=today,
        )
    )

    recent_7_day_total = (
        recent_7_day_records.aggregate(
            total=Sum("amount_collected")
        )["total"]
        or Decimal("0.00")
    )

    recent_7_day_count = (
        recent_7_day_records.count()
    )

    if recent_7_day_count:

        recent_7_day_average = (
            recent_7_day_total /
            Decimal(recent_7_day_count)
        )

    else:

        recent_7_day_average = (
            Decimal("0.00")
        )

    # =================================================
    # RECENT 30-DAY AVERAGE
    # =================================================

    thirty_days_ago = (
        today - timedelta(days=29)
    )

    recent_30_day_records = (
        DailyEarning.objects
        .filter(
            date__gte=thirty_days_ago,
            date__lte=today,
        )
    )

    recent_30_day_total = (
        recent_30_day_records.aggregate(
            total=Sum("amount_collected")
        )["total"]
        or Decimal("0.00")
    )

    recent_30_day_count = (
        recent_30_day_records.count()
    )

    if recent_30_day_count:

        recent_30_day_average = (
            recent_30_day_total /
            Decimal(recent_30_day_count)
        )

    else:

        recent_30_day_average = (
            Decimal("0.00")
        )

    # =================================================
    # SMART FORECAST RATE
    #
    # Prefer recent performance.
    #
    # If we have 7-day data:
    #     70% recent 7-day average
    #     30% lifetime average
    #
    # If not enough recent data:
    #     use lifetime average.
    # =================================================

    if recent_7_day_count >= 3:

        forecast_daily_average = (
            (
                recent_7_day_average *
                Decimal("0.70")
            )
            +
            (
                average_daily_earnings *
                Decimal("0.30")
            )
        )

    elif recent_30_day_count >= 3:

        forecast_daily_average = (
            (
                recent_30_day_average *
                Decimal("0.70")
            )
            +
            (
                average_daily_earnings *
                Decimal("0.30")
            )
        )

    else:

        forecast_daily_average = (
            average_daily_earnings
        )

    # =================================================
    # TREND ANALYSIS
    # =================================================

    if (
        recent_7_day_average > 0
        and recent_30_day_average > 0
    ):

        difference = (
            recent_7_day_average -
            recent_30_day_average
        )

        trend_percentage = (
            (
                difference /
                recent_30_day_average
            )
            * Decimal("100")
        )

        if trend_percentage >= Decimal("10"):

            trend = "Increasing"
            trend_symbol = "↑"

        elif trend_percentage <= Decimal("-10"):

            trend = "Decreasing"
            trend_symbol = "↓"

        else:

            trend = "Stable"
            trend_symbol = "→"

    else:

        trend = "Not enough data"
        trend_symbol = "—"
        trend_percentage = Decimal("0.00")

    # =================================================
    # BEST EARNING DAY
    # =================================================

    highest_earning = (
        DailyEarning.objects
        .order_by("-amount_collected")
        .first()
    )

    # =================================================
    # MONTHLY PROJECTION
    # =================================================

    days_elapsed = today.day

    if days_elapsed > 0:

        daily_month_average = (
            monthly_earnings /
            Decimal(days_elapsed)
        )

        projected_monthly_earnings = (
            daily_month_average *
            Decimal(month_end.day)
        )

    else:

        projected_monthly_earnings = (
            Decimal("0.00")
        )

    # =================================================
    # FUTURE EARNINGS FORECAST
    # =================================================

    forecast_tomorrow = (
        forecast_daily_average
    )

    forecast_7_days = (
        forecast_daily_average *
        Decimal("7")
    )

    forecast_30_days = (
        forecast_daily_average *
        Decimal("30")
    )

    # =================================================
    # EXPENSE FORECAST
    # =================================================

    expense_count = (
        Expense.objects.count()
    )

    if expense_count:

        average_daily_expenses = (
            total_expenses /
            Decimal(expense_count)
        )

    else:

        average_daily_expenses = (
            Decimal("0.00")
        )

    forecast_7_days_expenses = (
        average_daily_expenses *
        Decimal("7")
    )

    forecast_30_days_expenses = (
        average_daily_expenses *
        Decimal("30")
    )

    forecast_7_days_profit = (
        forecast_7_days -
        forecast_7_days_expenses
    )

    forecast_30_days_profit = (
        forecast_30_days -
        forecast_30_days_expenses
    )

    # =================================================
    # TARGET FORECAST
    #
    # KSh 50,000
    # KSh 100,000
    # KSh 150,000
    # =================================================

    target_amounts = [
        Decimal("50000"),
        Decimal("100000"),
        Decimal("150000"),
    ]

    target_forecasts = []

    for target in target_amounts:

        if total_earnings >= target:

            target_forecasts.append(
                {
                    "target": target,
                    "reached": True,
                    "date": None,
                    "days": 0,
                }
            )

            continue

        if forecast_daily_average <= 0:

            target_forecasts.append(
                {
                    "target": target,
                    "reached": False,
                    "date": None,
                    "days": None,
                }
            )

            continue

        remaining = (
            target -
            total_earnings
        )

        estimated_days_decimal = (
            remaining /
            forecast_daily_average
        )

        estimated_days = max(
            1,
            int(
                estimated_days_decimal.to_integral_value(
                    rounding=ROUND_CEILING
                )
            ),
        )

        estimated_date = (
            today +
            timedelta(days=estimated_days)
        )

        target_forecasts.append(
            {
                "target": target,
                "reached": False,
                "date": estimated_date,
                "days": estimated_days,
            }
        )

    # =================================================
    # 7-DAY CHART
    # =================================================

    chart_labels = []
    chart_values = []

    for offset in range(6, -1, -1):

        chart_date = (
            today -
            timedelta(days=offset)
        )

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
                float(
                    earning.amount_collected
                )
            )

        else:

            chart_values.append(0)

    # =================================================
    # RECENT RECORDS
    # =================================================

    recent_records = (
        DailyEarning.objects.all()[:10]
    )

    recent_expenses = (
        Expense.objects.all()[:10]
    )

    # =================================================
    # CONTEXT
    # =================================================

    context = {

        # ---------------------------------------------
        # ALL TIME
        # ---------------------------------------------

        "total_earnings":
            total_earnings,

        "total_expenses":
            total_expenses,

        "total_profit":
            total_profit,

        # ---------------------------------------------
        # TODAY
        # ---------------------------------------------

        "today_earnings":
            today_earnings,

        "today_expenses":
            today_expenses,

        "today_profit":
            today_profit,

        # ---------------------------------------------
        # WEEK
        # ---------------------------------------------

        "week_start":
            week_start,

        "week_end":
            week_end,

        "weekly_earnings":
            weekly_earnings,

        "weekly_expenses":
            weekly_expenses,

        "weekly_profit":
            weekly_profit,

        # ---------------------------------------------
        # MONTH
        # ---------------------------------------------

        "month_start":
            month_start,

        "month_end":
            month_end,

        "monthly_earnings":
            monthly_earnings,

        "monthly_expenses":
            monthly_expenses,

        "monthly_profit":
            monthly_profit,

        # ---------------------------------------------
        # ANALYSIS
        # ---------------------------------------------

        "average_daily_earnings":
            average_daily_earnings,

        "recent_7_day_average":
            recent_7_day_average,

        "recent_30_day_average":
            recent_30_day_average,

        "highest_earning":
            highest_earning,

        "projected_monthly_earnings":
            projected_monthly_earnings,

        # ---------------------------------------------
        # SMART FORECAST
        # ---------------------------------------------

        "forecast_daily_average":
            forecast_daily_average,

        "forecast_tomorrow":
            forecast_tomorrow,

        "forecast_7_days":
            forecast_7_days,

        "forecast_30_days":
            forecast_30_days,

        "forecast_7_days_profit":
            forecast_7_days_profit,

        "forecast_30_days_profit":
            forecast_30_days_profit,

        "average_daily_expenses":
            average_daily_expenses,

        # ---------------------------------------------
        # TREND
        # ---------------------------------------------

        "trend":
            trend,

        "trend_symbol":
            trend_symbol,

        "trend_percentage":
            trend_percentage,

        # ---------------------------------------------
        # TARGET FORECAST
        # ---------------------------------------------

        "target_forecasts":
            target_forecasts,

        # ---------------------------------------------
        # CHART
        # ---------------------------------------------

        "chart_labels":
            chart_labels,

        "chart_values":
            chart_values,

        # ---------------------------------------------
        # RECORDS
        # ---------------------------------------------

        "recent_records":
            recent_records,

        "recent_expenses":
            recent_expenses,
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