"""Add fake members to the API."""
# Standard Python Libraries
from datetime import datetime, timedelta
import random
import warnings

# Third-Party Libraries
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from faker import Faker

# Custom Libraries
from api.models import Member, Rank

fake = Faker()

# Filter out the warning about time zone support.
warnings.filterwarnings(
    "ignore", category=RuntimeWarning, module="django.db.models.fields"
)


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
            # Attempt to create a member, and if a duplicate badge number error occurs, add one to the badge number
            while True:
                badge_num = random.randint(505000, 505999)
                first_name = fake.first_name()
                last_name = fake.last_name()
                rank = random.choice(ranks)  # Choose a random rank instance

                created_date = fake.date_time_between_dates(
                    datetime(2021, 6, 1), datetime.today() - timedelta(days=1)
                )
                updated_date = fake.date_time_between_dates(
                    created_date, datetime.today()
                )

                try:
                    member = Member(
                        badge_num=badge_num,
                        created=created_date,
                        first_name=first_name,
                        last_name=last_name,
                        rank=rank,
                        updated=updated_date,
                    )
                    member.save()
                    members.append(member)
                    break  # Break the loop if member creation is successful

                except IntegrityError as e:
                    if "Duplicate entry" in str(e):
                        # Increment the badge number and try again
                        badge_num += 1
                        continue
                    else:
                        # Handle other IntegrityError exceptions if necessary
                        self.stdout.write(
                            self.style.ERROR(f"An error occurred: {str(e)}")
                        )
                        break

        self.stdout.write(
            self.style.SUCCESS(f"Added {len(members)} fake members to the database.")
        )
