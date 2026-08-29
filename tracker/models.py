from django.db import models


class DailyEarning(models.Model):
    date = models.DateField(
        unique=True
    )

    amount_collected = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return (
            f"{self.date} - "
            f"KSh {self.amount_collected}"
        )


class Expense(models.Model):

    EXPENSE_TYPE_CHOICES = [
        (
            "SALARY",
            "Salary",
        ),
        (
            "ELECTRICITY",
            "Electricity",
        ),
        (
            "RENT",
            "Rent",
        ),
        (
            "POLICE",
            "Police",
        ),
        (
            "OTHERS",
            "Others",
        ),
        (
            "MAINTENANCE",
            "Maintenance",
        ),
    ]

    date = models.DateField()

    expense_type = models.CharField(
        max_length=20,
        choices=EXPENSE_TYPE_CHOICES,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return (
            f"{self.get_expense_type_display()} - "
            f"{self.date} - "
            f"KSh {self.amount}"
        )