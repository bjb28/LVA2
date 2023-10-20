"""Add fake members to the API."""
# Standard Python Libraries
from datetime import datetime, timedelta
import random

# Third-Party Libraries
from django.core.management.base import BaseCommand
from faker import Faker

# Custom Libraries
from api.models import Member, Rank

fake = Faker()


class Command(BaseCommand):
    """Creates fake members in the database."""

    help = "Add fake members to the database"

    def add_arguments(self, parser):
        """Argument parser."""
        parser.add_argument(
            "num_members", type=int, help="Number of fake members to generate"
        )

    def handle(self, *args, **kwargs):
        """Handle action."""
        num_members = kwargs["num_members"]

        if num_members <= 0:
            self.stdout.write(
                self.style.WARNING(
                    "Please provide a valid positive number of members to generate."
                )
            )
            return

        ranks = Rank.objects.all()  # Fetch all rank instances

        if not ranks:
            self.stdout.write(
                self.style.WARNING(
                    "No ranks found in the database. Ensure you have ranks in the Rank model."
                )
            )
            return

        members = []

        for _ in range(num_members):
            badge_num = random.randint(505000, 505999)
            first_name = fake.first_name()
            last_name = fake.last_name()
            rank = random.choice(ranks)  # Choose a random rank instance

            created_date = fake.date_time_between_dates(
                datetime(2021, 6, 1), datetime.today() - timedelta(days=1)
            )
            updated_date = fake.date_time_between_dates(created_date, datetime.today())

            member = Member(
                badge_num=badge_num,
                created=created_date,
                first_name=first_name,
                last_name=last_name,
                rank=rank,
                updated=updated_date,
            )
            members.append(member)

        Member.objects.bulk_create(members)
        self.stdout.write(
            self.style.SUCCESS(f"Added {num_members} fake members to the database.")
        )
