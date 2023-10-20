"""Add fake collateral duties to the API."""
# Standard Python Libraries
from datetime import datetime, timedelta
import random
import warnings

# Third-Party Libraries
from django.core.management.base import BaseCommand
from faker import Faker

# Custom Libraries
from api.models import CollateralDuty, Committee, HourType, Member

fake = Faker()

# Filter out the warning about time zone support.
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, module="django.db.models.fields"
)


class Command(BaseCommand):
    """Create fake collateral duties."""

    help = "Add Collateral Duty records for members in the database"

    def add_arguments(self, parser):
        """Argument parser."""
        parser.add_argument(
            "num_collateral_duties",
            type=int,
            help="Number of Collateral Duty records to add per member",
        )

    def handle(self, *args, **kwargs):
        """Handle action."""
        num_collateral_duties = kwargs["num_collateral_duties"]

        if num_collateral_duties <= 0:
            self.stdout.write(
                self.style.WARNING(
                    "Please provide valid positive numbers for num_collateral_duties."
                )
            )
            return

        members = Member.objects.all()
        committees = Committee.objects.all()

        if not members:
            self.stdout.write(self.style.WARNING("No members found in the database."))
            return

        collateral_duty_records = []

        for member in members:
            for _ in range(random.randint(1, num_collateral_duties)):
                start_time = fake.date_time_between_dates(
                    datetime(2022, 1, 1), datetime(2023, 12, 31)
                )

                end_time = start_time + timedelta(hours=random.randint(4, 6))

                committee = random.choice(committees)
                description = fake.text(max_nb_chars=10)

                collateral_duty_record = CollateralDuty(
                    badge_num=member,
                    start_time=start_time,
                    end_time=end_time,
                    type=HourType.objects.filter(name="Collateral Duty").first(),
                    losap_valid=1,
                    committee=committee,
                    description=description,
                )
                collateral_duty_records.append(collateral_duty_record)

        CollateralDuty.objects.bulk_create(collateral_duty_records)
        self.stdout.write(
            self.style.SUCCESS(
                f"Added {len(collateral_duty_records)} Collateral Duty records."
            )
        )
