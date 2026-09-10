from decimal import Decimal

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import DailyEarning, Expense, CoinCollection, Profile


class DailyEarningForm(forms.ModelForm):

    class Meta:
        model = DailyEarning

        fields = [
            "date",
            "amount_collected",
            "notes",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "amount_collected": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Enter amount collected",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Optional notes",
                }
            ),
        }


class ExpenseForm(forms.ModelForm):

    class Meta:
        model = Expense

        fields = [
            "date",
            "expense_type",
            "amount",
            "notes",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "expense_type": forms.Select(),
            "amount": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Enter expense amount",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Optional notes",
                }
            ),
        }


class CoinCollectionForm(forms.ModelForm):

    class Meta:
        model = CoinCollection

        fields = [
            "collection_date",
            "coins_collected",
            "actual_m_pesa",
            "notes",
        ]

        widgets = {
            "collection_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "coins_collected": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "1",
                    "placeholder": "Enter number of coins",
                    "id": "id_coins_collected",
                    "inputmode": "numeric",
                }
            ),
            "actual_m_pesa": forms.NumberInput(
                attrs={
                    "min": "0",
                    "step": "0.01",
                    "placeholder": "Enter actual M-Pesa amount",
                    "inputmode": "decimal",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Optional collection notes",
                }
            ),
        }

    def save(self, commit=True):
        collection = super().save(commit=False)

        # Fixed default coin value: KSh 20
        collection.coin_value = Decimal("20.00")

        if commit:
            collection.save()

        return collection


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email address",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = User

        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

        widgets = {
            "username": forms.TextInput(
                attrs={
                    "placeholder": "Choose a username",
                    "autocomplete": "username",
                }
            ),
        }


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = [
            "profile_picture",
        ]

        widgets = {
            "profile_picture": forms.ClearableFileInput(
                attrs={
                    "accept": "image/*",
                }
            ),
        }
