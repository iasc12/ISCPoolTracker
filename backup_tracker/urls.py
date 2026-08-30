from django.urls import path

from .views import (
    dashboard,

    add_earning,
    earnings_list,
    edit_earning,
    delete_earning,

    add_expense,
    expenses_list,
    edit_expense,
    delete_expense,

    reports,
    generate_report,
)


urlpatterns = [

    # Dashboard
    path(
        "",
        dashboard,
        name="dashboard",
    ),

    # Earnings
    path(
        "earnings/add/",
        add_earning,
        name="add_earning",
    ),

    path(
        "earnings/",
        earnings_list,
        name="earnings_list",
    ),

    path(
        "earnings/<int:earning_id>/edit/",
        edit_earning,
        name="edit_earning",
    ),

    path(
        "earnings/<int:earning_id>/delete/",
        delete_earning,
        name="delete_earning",
    ),

    # Expenses
    path(
        "expenses/add/",
        add_expense,
        name="add_expense",
    ),

    path(
        "expenses/",
        expenses_list,
        name="expenses_list",
    ),

    path(
        "expenses/<int:expense_id>/edit/",
        edit_expense,
        name="edit_expense",
    ),

    path(
        "expenses/<int:expense_id>/delete/",
        delete_expense,
        name="delete_expense",
    ),

    # Reports
    path(
        "reports/",
        reports,
        name="reports",
    ),

    path(
        "reports/generate/",
        generate_report,
        name="generate_report",
    ),
]