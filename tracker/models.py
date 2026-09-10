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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return (
            f"{self.get_expense_type_display()} - "
            f"{self.date} - KSh {self.amount}"
        )


class Notification(models.Model):

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class CoinCollection(models.Model):
    """
    Records coins physically removed from the pool tables.

    Business logic:

    Current coins collected determine the expected amount
    for the NEXT collection.

    The previous collection's coins determine the expected
    amount for the CURRENT collection.
    """

    collection_date = models.DateField()

    coins_collected = models.PositiveIntegerField(
        help_text=(
            "Number of coins physically removed "
            "from the pool tables."
        )
    )

    coin_value = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=20.00,
        help_text="Value of one coin in KSh."
    )

    actual_m_pesa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=(
            "Actual M-Pesa amount received "
            "for this collection."
        )
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = [
            "-collection_date",
            "-created_at"
        ]

    def __str__(self):
        return (
            f"{self.collection_date} - "
            f"{self.coins_collected} coins"
        )

    @property
    def previous_collection(self):
        """
        Finds the collection immediately before this one.
        """

        if not self.pk:
            return None

        return (
            CoinCollection.objects
            .filter(
                models.Q(
                    collection_date__lt=self.collection_date
                )
                |
                models.Q(
                    collection_date=self.collection_date,
                    created_at__lt=self.created_at
                )
            )
            .order_by(
                "-collection_date",
                "-created_at"
            )
            .first()
        )

    @property
    def expected_amount(self):
        """
        Expected money for THIS collection.

        This comes from the previous collection.

        Example:

        Previous collection = 100 coins
        Coin value = KSh 20

        Expected current collection =
        100 × 20 = KSh 2,000
        """

        previous = self.previous_collection

        if not previous:
            return 0

        return (
            previous.coins_collected *
            previous.coin_value
        )

    @property
    def next_expected_amount(self):
        """
        Expected money for the NEXT collection.

        Current coins × current coin value.
        """

        return (
            self.coins_collected *
            self.coin_value
        )

    @property
    def difference(self):
        """
        Actual M-Pesa minus expected money.
        """

        if self.actual_m_pesa is None:
            return None

        return (
            self.actual_m_pesa -
            self.expected_amount
        )

    @property
    def collection_rate(self):
        """
        Percentage of expected money actually received.
        """

        if (
            self.actual_m_pesa is None
            or self.expected_amount <= 0
        ):
            return None

        return (
            self.actual_m_pesa /
            self.expected_amount
        ) * 100

    @property
    def coin_change(self):
        """
        Difference between current coins and
        previous collection's coins.
        """

        previous = self.previous_collection

        if not previous:
            return None

        return (
            self.coins_collected -
            previous.coins_collected
        )
from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Membership(models.Model):

    STATUS_TRIAL = "trial"
    STATUS_ACTIVE = "active"
    STATUS_EXPIRED = "expired"

    STATUS_CHOICES = [
        (STATUS_TRIAL, "Free Trial"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_EXPIRED, "Expired"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="membership",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_TRIAL,
    )

    trial_started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    trial_ends_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    membership_started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    membership_ends_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

    @property
    def is_active(self):
        from django.utils import timezone

        now = timezone.now()

        if self.status == self.STATUS_TRIAL:
            return bool(
                self.trial_ends_at
                and now <= self.trial_ends_at
            )

        if self.status == self.STATUS_ACTIVE:
            return bool(
                self.membership_ends_at
                and now <= self.membership_ends_at
            )

        return False
