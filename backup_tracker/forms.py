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
