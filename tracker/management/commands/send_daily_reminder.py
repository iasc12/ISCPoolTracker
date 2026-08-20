from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mail


class Command(BaseCommand):
    help = "Send the daily ISC Pool Tracker earnings reminder."

    def handle(self, *args, **options):

        recipient = (
            getattr(
                settings,
                "POOL_TRACKER_REMINDER_EMAIL",
                "",
            )
            or getattr(
                settings,
                "EMAIL_HOST_USER",
                "",
            )
        )

        if not recipient:
            self.stdout.write(
                self.style.ERROR(
                    "No reminder email address configured."
                )
            )
            return

        subject = "ISC Pool Tracker — Daily Reminder"

        message = (
            "Hello,\n\n"
            "This is your daily ISC Pool Tracker reminder.\n\n"
            "Please enter today's pool table earnings "
            "into the system.\n\n"
            "Remember to record any expenses as well, "
            "including:\n"
            "- Employee Payment\n"
            "- Police Payment\n"
            "- Fuel\n"
            "- Other Expense\n\n"
            "ISC Pool Tracker"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Daily reminder sent to {recipient}"
                )
            )

        except Exception as exc:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to send reminder: {exc}"
                )
            )