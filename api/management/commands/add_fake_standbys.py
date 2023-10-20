"""Add fake stand bys to the API."""
# Standard Python Libraries
from datetime import datetime, timedelta
import random
import warnings

# Third-Party Libraries
from django.core.management.base import BaseCommand
from faker import Faker

# Custom Libraries
from api.models import HourType, Member, StandBy

fake = Faker()

# Filter out the warning about time zone support.
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, module="django.db.models.fields"
)


class Command(BaseCommand):
    """Create fake stand bys."""

    help = "Add StandBy records for members in the database"

    def add_arguments(self, parser):
        """Argument parser."""
        parser.add_argument(
            "num_standbys", type=int, help="Number of StandBy records to add per member"
        )

    def handle(self, *args, **kwargs):
        """Handle action."""
        num_standbys = kwargs["num_standbys"]

        if num_standbys <= 0:
            self.stdout.write(
                self.style.WARNING(
                    "Please provide valid positive numbers for num_standbys."
                )
            )
            return

        members = Member.objects.all()

        if not members:
            self.stdout.write(self.style.WARNING("No members found in the database."))
            return

        standby_records = []

        for member in members:
            for _ in range(random.randint(1, num_standbys)):
                start_time = fake.date_time_between_dates(
                    datetime(2022, 1, 1), datetime(2023, 12, 31)
                )

                end_time = start_time + timedelta(hours=random.randint(4, 6))

                standby_record = StandBy(
                    badge_num=member,
                    start_time=start_time,
                    end_time=end_time,
                    type=HourType.objects.filter(name="Stand By").first(),
                    losap_valid=1,
                )
                standby_records.append(standby_record)

        StandBy.objects.bulk_create(standby_records)
        self.stdout.write(
            self.style.SUCCESS(f"Added {len(standby_records)} StandBy records.")
        )
