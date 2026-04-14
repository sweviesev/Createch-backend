from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from marketplace.models import (
    Block,
    Category,
    Creator,
    DailyAnalytics,
    DeadlineNotification,
    Follow,
    Match,
    Message,
    Order,
    OrderTimeline,
    PaymentMethod,
    Report,
    Review,
    Service,
    SupportTicket,
    User,
    UserWallet,
    Withdrawal,
)


class Command(BaseCommand):
    help = 'Create unmanaged marketplace tables for local SQLite development.'

    def handle(self, *args, **options):
        if connection.vendor != 'sqlite' or not getattr(settings, 'USE_SQLITE', False):
            raise CommandError('bootstrap_local_db is only intended for local SQLite mode.')

        models_to_create = [
            User,
            Creator,
            Category,
            Service,
            Order,
            OrderTimeline,
            Review,
            Message,
            Follow,
            Block,
            Report,
            Match,
            PaymentMethod,
            SupportTicket,
            UserWallet,
            Withdrawal,
            DeadlineNotification,
            DailyAnalytics,
        ]

        existing_tables = set(connection.introspection.table_names())
        created = []

        with connection.schema_editor() as schema_editor:
            for model in models_to_create:
                table_name = model._meta.db_table
                if table_name in existing_tables:
                    continue
                schema_editor.create_model(model)
                existing_tables.add(table_name)
                created.append(table_name)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created {len(created)} local tables.'))
            for table_name in created:
                self.stdout.write(f'  - {table_name}')
        else:
            self.stdout.write(self.style.SUCCESS('Local tables already exist.'))
