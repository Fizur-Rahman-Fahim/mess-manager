from django.core.management.base import BaseCommand

from meals.services.meal import create_default_meals_for_active_members


class Command(BaseCommand):
    help = 'Create default meal rows (all on) for active members for upcoming days.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days ahead from today to create rows (default: 30).',
        )

    def handle(self, *args, **options):
        days = options['days']
        created = create_default_meals_for_active_members(days_ahead=days)
        self.stdout.write(
            self.style.SUCCESS(f'Created {created} daily meal row(s) for the next {days} days.')
        )
