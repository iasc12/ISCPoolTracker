from django.urls import path

from .views import (
    add_earning,
    add_expense,
    dashboard,
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
        "expenses/add/",
        add_expense,
        name="add_expense",
    ),
]