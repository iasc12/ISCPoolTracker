from django import forms

from .models import DailyEarning, Expense


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
                    "placeholder": "Enter amount collected",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "placeholder": "Optional notes",
                    "rows": 3,
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
            "amount": forms.NumberInput(
                attrs={
                    "placeholder": "Enter amount",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "placeholder": "Optional notes",
                    "rows": 3,
                }
            ),
        }