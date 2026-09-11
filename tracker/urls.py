from django.urls import path

from .views import (
    register,
    membership,
    membership_approvals,
    membership_approval_action,
    pay_membership,
    mpesa_callback,
    dashboard,
    profile,
    edit_profile,
    change_password,
    settings_page,
    history,

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

    coin_collection_list,
    add_coin_collection,
    edit_coin_collection,
    delete_coin_collection,
)


urlpatterns = [

    path("register/", register, name="register"),

    path("", dashboard, name="dashboard"),

    path("history/", history, name="history"),

    path("settings/", settings_page, name="settings"),

    path("membership/", membership, name="membership"),

    path(
        "membership/pay/",
        pay_membership,
        name="pay_membership",
    ),

    path(
        "membership/approvals/",
        membership_approvals,
        name="membership_approvals",
    ),

    path(
        "membership/approvals/<int:payment_id>/<str:action>/",
        membership_approval_action,
        name="membership_approval_action",
    ),

    path(
        "mpesa/callback/",
        mpesa_callback,
        name="mpesa_callback",
    ),

    path("profile/", profile, name="profile"),

    path(
        "profile/edit/",
        edit_profile,
        name="edit_profile",
    ),

    path(
        "profile/password/",
        change_password,
        name="change_password",
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

    path(
        "reports/generate/",
        generate_report,
        name="generate_report",
    ),

    path(
        "coins/",
        coin_collection_list,
        name="coin_collections",
    ),

    path(
        "coins/add/",
        add_coin_collection,
        name="add_coin_collection",
    ),

    path(
        "coins/<int:collection_id>/edit/",
        edit_coin_collection,
        name="edit_coin_collection",
    ),

    path(
        "coins/<int:collection_id>/delete/",
        delete_coin_collection,
        name="delete_coin_collection",
    ),
]
