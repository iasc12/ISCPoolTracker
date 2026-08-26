from django.urls import path

from .views import (
    dashboard,
    add_earning,
    add_expense,
    earnings_list,
    edit_earning,
    delete_earning,
    expenses_list,
    edit_expense,
    delete_expense,
    reports,
)

urlpatterns = [

    path(
        "",
        dashboard,
        name="dashboard",
    ),

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
    path(
    "reports/",
    reports,
    name="reports",
),
]