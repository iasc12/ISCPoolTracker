from django.db import models
from django.contrib.auth.models import User


class DailyEarning(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="daily_earnings",
    )

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

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="expenses",
    )

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

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coin_collections",
    )

    """
    Records the physical coins collected from the pool tables.

    Business logic:

    One coin is worth KSh 20.

    Expected M-Pesa for a collection is calculated directly
    from the number of coins collected:

        coins_collected × coin_value

    The actual M-Pesa amount is entered by the collector.
    """

    collection_date = models.DateField()

    coins_collected = models.PositiveIntegerField(
        help_text=(
            "Number of coins physically removed "
            "from the pool tables."
        )
    )

    additional_coins = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Additional coins found or collected "
            "outside the main collection."
        )
    )

    lost_coins = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Coins lost, missing, or otherwise "
            "unaccounted for."
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
    def coin_amount(self):
        """
        Expected M-Pesa amount based on the coins
        physically collected.
        """

        return (
            self.coins_collected *
            self.coin_value
        )

    @property
    def expected_amount(self):
        """
        Expected M-Pesa for THIS collection.

        This is based directly on the current
        collection's coins.
        """

        return self.coin_amount

    @property
    def next_expected_amount(self):
        """
        Compatibility property.

        The current collection's coins determine
        the calculated amount.
        """

        return self.coin_amount

    @property
    def difference(self):
        """
        Actual M-Pesa minus the expected coin amount.

        Positive = more M-Pesa than expected.
        Negative = less M-Pesa than expected.
        Zero = exact collection.
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
        Percentage of the expected coin amount
        that was actually received through M-Pesa.
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
        Net coin adjustment.

        Additional coins increase the count while
        lost coins reduce it.

        Retained for compatibility with existing
        dashboard/template code.
        """

        return (
            self.additional_coins -
            self.lost_coins
        )

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

class MpesaPayment(models.Model):

    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="mpesa_payments",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    phone_number = models.CharField(
        max_length=20,
    )

    merchant_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    checkout_request_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
    )

    mpesa_receipt_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    result_code = models.IntegerField(
        blank=True,
        null=True,
    )

    result_description = models.TextField(
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"KSh {self.amount} - "
            f"{self.get_status_display()}"
        )
