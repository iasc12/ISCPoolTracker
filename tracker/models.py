from django.db import models


class DailyEarning(models.Model):
    date = models.DateField()
    amount_collected = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.date} - KSh {self.amount_collected}"


class Expense(models.Model):

    EXPENSE_TYPE_CHOICES = [
        ("EMPLOYEE", "Employee Payment"),
        ("POLICE", "Police Payment"),
        ("FUEL", "Fuel"),
        ("ELECTRICITY", "Electricity"),
        ("RENT", "Rent"),
        ("MAINTENANCE", "Maintenance"),
        ("OTHERS", "Other Expense"),
    ]

    date = models.DateField()
    expense_type = models.CharField(
        max_length=20,
        choices=EXPENSE_TYPE_CHOICES
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return (
            f"{self.get_expense_type_display()} - "
            f"{self.date} - KSh {self.amount}"
        )
