import os
import time
import psycopg2

from django.db import connections
from django.core.management import BaseCommand
from django.db.utils import OperationalError


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None

        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, waititng 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))

        db_name = os.getenv('DB_NAME')
        conn = psycopg2.connect(
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database='postgres',
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = '{0}'".format(db_name))

        if cursor.fetchone() is None:
            self.stdout.write('creating database...')
            cursor.execute("CREATE DATABASE {}".format(db_name))
            self.stdout.write(self.style.SUCCESS('Database is created'))

        conn.close()
