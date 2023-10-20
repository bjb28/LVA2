"""Add fake sleep ins to the API."""
# Standard Python Libraries
from datetime import datetime
import random
import warnings

# Third-Party Libraries
from django.core.management.base import BaseCommand
from faker import Faker

# Custom Libraries
from api.models import HourType, Member, SleepIn

fake = Faker()

# Filter out the warning about time zone support.
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, module="django.db.models.fields"
)


class Command(BaseCommand):
    """Creates fake Sleep Ins."""

    help = "Add sleep-ins for members in the database"

    def add_arguments(self, parser):
        """Argument parser."""
        parser.add_argument(
            "max_sleep_ins", type=int, help="Maximum number of sleep-ins per member"
        )

    def handle(self, *args, **kwargs):
        """Handle action."""
        max_sleep_ins = kwargs["max_sleep_ins"]

        if max_sleep_ins <= 0:
            self.stdout.write(
                self.style.WARNING(
                    "Please provide valid positive numbers for max_sleep_ins."
                )
            )
            return

        members = Member.objects.all()

        if not members:
            self.stdout.write(self.style.WARNING("No members found in the database."))
            return

        sleep_ins = []

        for member in members:

            for _ in range(random.randint(1, max_sleep_ins)):
                sleep_in_date = fake.date_time_between_dates(
                    datetime(2022, 1, 1), datetime(2023, 12, 31)
                )

                sleep_in = SleepIn(
                    badge_num=member,
                    date=sleep_in_date,
                    type=HourType.objects.filter(name="Sleep In").first(),
                )
                sleep_ins.append(sleep_in)

        SleepIn.objects.bulk_create(sleep_ins)
        self.stdout.write(self.style.SUCCESS(f"Added {len(sleep_ins)} sleep-ins."))
