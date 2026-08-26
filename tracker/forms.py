from django import forms

from .models import DailyEarning, Expense


class DailyEarningForm(forms.ModelForm):

    class Meta:

        model = DailyEarning

        fields = [
            "amount_collected",
            "notes",
        ]

        widgets = {

            "amount_collected": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter today's earnings",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-input",
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
                    "class": "form-input",
                    "type": "date",
                }
            ),

            "expense_type": forms.Select(
                attrs={
                    "class": "form-input",
                }
            ),

            "amount": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Enter amount",
                    "step": "0.01",
                    "min": "0",
                }
            ),

            "notes": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "placeholder": "Optional notes",
                    "rows": 3,
                }
            ),
        }
